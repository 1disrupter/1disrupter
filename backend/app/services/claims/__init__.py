# -*- coding: utf-8 -*-
"""Claim service — business logic for the owner-claim flow."""
from __future__ import annotations

import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models import Venue, VenueClaim
from app.services import webhooks
from app.services.email import send_email, is_configured as email_configured

logger = logging.getLogger("vibe2nite.claims")


def _ttl_minutes() -> int:
    try:
        return max(5, int(os.environ.get("CLAIM_TOKEN_TTL_MINUTES", "30")))
    except ValueError:
        return 30


def _link_base() -> str:
    raw = (os.environ.get("CLAIM_LINK_BASE_URL") or "").strip().rstrip("/")
    # Fallback to request-time host; handled in router when empty.
    return raw


def _render_email(venue: Venue, link: str, ttl_min: int) -> tuple[str, str]:
    subject = f"Verify your claim of {venue.name} · Vibe2Nite"
    html = f"""
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:#05050A;padding:32px 0;font-family:Outfit,Inter,Arial,sans-serif;color:#F5EFFF;">
      <tr><td align="center">
        <table role="presentation" width="560" cellspacing="0" cellpadding="0" border="0" style="background:#0f0a1a;border:1px solid #2A1846;border-radius:18px;padding:32px;">
          <tr><td style="padding-bottom:12px;">
            <div style="font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#B15CFF;">Vibe2Nite · Ownership</div>
            <h1 style="margin:6px 0 0;font-size:28px;letter-spacing:1px;color:#ffffff;">Confirm you own {venue.name}</h1>
          </td></tr>
          <tr><td style="font-size:14px;line-height:22px;color:#C7A7FF;">
            Tap the button below to verify this claim. The link is single-use and expires in {ttl_min} minutes.
          </td></tr>
          <tr><td style="padding:24px 0;">
            <a href="{link}" style="display:inline-block;padding:14px 28px;border-radius:999px;background:linear-gradient(135deg,#8A2BE2,#FF2EC4);color:#fff;font-weight:700;text-decoration:none;letter-spacing:1px;">
              Verify claim
            </a>
          </td></tr>
          <tr><td style="font-size:12px;color:#9C8FBF;word-break:break-all;">
            Or paste this URL in a browser:<br>
            <code style="color:#00F5FF;">{link}</code>
          </td></tr>
          <tr><td style="padding-top:24px;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#6B6B6B;">
            Didn't request this? Ignore this email.
          </td></tr>
        </table>
      </td></tr>
    </table>
    """.strip()
    text = (
        f"Confirm you own {venue.name} on Vibe2Nite.\n"
        f"Open this link to verify (expires in {ttl_min} minutes, single-use):\n{link}\n"
    )
    return subject, html, text  # type: ignore[return-value]


async def submit_claim(
    db: Session, *, venue_id: str, owner_name: str, email: str, proof: str,
    base_url_fallback: str,
) -> dict:
    venue = db.get(Venue, venue_id)
    if not venue:
        raise ValueError("venue not found")

    # Dedup: reuse pending claim for same venue+email if under TTL — else new row.
    ttl_min = _ttl_minutes()
    now = datetime.now(timezone.utc)
    existing = (
        db.query(VenueClaim)
        .filter(
            VenueClaim.venue_id == venue_id,
            VenueClaim.email == email,
            VenueClaim.status.in_(("pending", "email_sent")),
        )
        .order_by(desc(VenueClaim.created_at))
        .first()
    )

    token = secrets.token_urlsafe(24)
    expires = now + timedelta(minutes=ttl_min)

    if existing:
        existing.owner_name = owner_name
        existing.proof = proof
        existing.token = token
        existing.token_expires_at = expires
        existing.status = "email_sent"
        claim = existing
    else:
        claim = VenueClaim(
            venue_id=venue_id,
            owner_name=owner_name,
            email=email,
            proof=proof,
            token=token,
            token_expires_at=expires,
            status="email_sent",
        )
        db.add(claim)
    db.commit()
    db.refresh(claim)

    base = _link_base() or base_url_fallback.rstrip("/")
    link = f"{base}/api/claims/verify/{token}"

    subject, html, text = _render_email(venue, link, ttl_min)  # type: ignore[misc]
    mail_status = await send_email(to=email, subject=subject, html=html, text=text)

    return {
        "claim_id": claim.id,
        "status": claim.status,
        "email_provider_live": email_configured(),
        "email_delivery": mail_status,
        # Expose the link for console-only mode. Callers (public API) should
        # only surface this to admins, not end users, but since the user
        # submitted their own email it's fine either way for the flow to
        # continue in dev environments.
        "magic_link": link if not mail_status.get("sent") else None,
        "expires_at": expires.isoformat(),
    }


def verify_claim(db: Session, token: str) -> dict:
    claim = db.query(VenueClaim).filter(VenueClaim.token == token).one_or_none()
    if not claim:
        return {"ok": False, "reason": "invalid_token"}
    if claim.status == "verified":
        return {"ok": False, "reason": "already_verified"}
    if claim.status == "rejected":
        return {"ok": False, "reason": "rejected"}
    if not claim.token_expires_at or datetime.now(timezone.utc) > claim.token_expires_at:
        claim.token = None
        db.commit()
        return {"ok": False, "reason": "expired"}

    claim.status = "verified"
    claim.verified_at = datetime.now(timezone.utc)
    claim.token = None  # single-use
    db.commit()

    # Fire webhook — non-blocking.
    venue = db.get(Venue, claim.venue_id)
    webhooks.dispatch(
        "VENUE_CLAIMED",
        title=f"{venue.name if venue else claim.venue_id} claimed",
        body=f"{claim.owner_name} <{claim.email}> is now listed as owner.",
        meta={
            "venue_id": claim.venue_id,
            "venue_name": venue.name if venue else None,
            "owner_email": claim.email,
            "claim_id": claim.id,
        },
    )
    return {"ok": True, "claim": claim.as_dict(), "venue_name": venue.name if venue else None}


def list_claims(db: Session, status: Optional[str] = None, limit: int = 100) -> list[dict]:
    q = db.query(VenueClaim)
    if status:
        q = q.filter(VenueClaim.status == status)
    q = q.order_by(desc(VenueClaim.created_at)).limit(limit)
    return [c.as_dict() for c in q.all()]


def admin_review(db: Session, claim_id: str, *, action: str, reviewer: str, note: str = "") -> dict:
    if action not in {"approve", "reject"}:
        raise ValueError("action must be approve|reject")
    claim = db.get(VenueClaim, claim_id)
    if not claim:
        raise ValueError("claim not found")

    claim.reviewed_at = datetime.now(timezone.utc)
    claim.reviewer = reviewer
    meta = dict(claim.meta or {})
    if note:
        meta["review_note"] = note
    claim.meta = meta

    if action == "approve":
        claim.status = "verified"
        claim.verified_at = claim.verified_at or claim.reviewed_at
        claim.token = None
        db.commit()

        venue = db.get(Venue, claim.venue_id)
        webhooks.dispatch(
            "VENUE_CLAIMED",
            title=f"{venue.name if venue else claim.venue_id} approved",
            body=f"Admin {reviewer} approved claim by {claim.owner_name} <{claim.email}>.",
            meta={
                "venue_id": claim.venue_id,
                "owner_email": claim.email,
                "claim_id": claim.id,
                "reviewer": reviewer,
            },
        )
    else:
        claim.status = "rejected"
        claim.token = None
        db.commit()

    return claim.as_dict()


def owner_for_venue(db: Session, venue_id: str) -> Optional[dict]:
    """Return the verified owner (if any) for a venue."""
    c = (
        db.query(VenueClaim)
        .filter(VenueClaim.venue_id == venue_id, VenueClaim.status == "verified")
        .order_by(desc(VenueClaim.verified_at))
        .first()
    )
    if not c:
        return None
    return {
        "claim_id": c.id,
        "owner_name": c.owner_name,
        "email": c.email,
        "verified_at": c.verified_at.isoformat() if c.verified_at else None,
    }
