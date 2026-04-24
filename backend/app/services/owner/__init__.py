# -*- coding: utf-8 -*-
"""Owner service — verified-owner API-key auth, venue-handle management, dashboard.

Auth model: on claim verification we mint an opaque `owner_api_key` stored in
`VenueClaim.meta["api_key"]`. The owner sends it via `X-Owner-Key` header; the
router resolves the key to the owning claim (and therefore the venue(s)).
"""
from __future__ import annotations

import logging
import secrets
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models import Venue, VenueClaim, VenueSignals, Vibe
from app.models.launch import NotificationLog, VenueProfile

logger = logging.getLogger("vibe2nite.owner")


# ---------------------------------------------------------------------------
# Ownership lifecycle helpers (Iter 16)
# ---------------------------------------------------------------------------
def _get_expiry(claim: VenueClaim) -> Optional[datetime]:
    raw = (claim.meta or {}).get("ownership_expires_at")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw)
    except Exception:
        return None


def is_ownership_active(claim: VenueClaim) -> bool:
    """A claim counts as actively verified when status=='verified' AND the
    ownership has not been explicitly expired. `needs_reverify` / `rejected`
    are never active. If an expiry is set and already past → inactive."""
    if claim.status != "verified":
        return False
    exp = _get_expiry(claim)
    if exp and exp <= datetime.now(timezone.utc):
        return False
    return True


def invalidate_api_key(db: Session, claim: VenueClaim) -> None:
    meta = dict(claim.meta or {})
    meta.pop("api_key", None)
    claim.meta = meta
    db.commit()


# ---------------------------------------------------------------------------
# Key lifecycle
# ---------------------------------------------------------------------------
def mint_api_key(db: Session, claim: VenueClaim) -> str:
    """Generate + persist an owner API key into the claim meta (idempotent)."""
    meta = dict(claim.meta or {})
    key = meta.get("api_key")
    if not key:
        # Spec: vk_<random 32 chars>. token_urlsafe(24) → ~32 chars.
        key = "vk_" + secrets.token_urlsafe(24)
        meta["api_key"] = key
        claim.meta = meta
        db.commit()
    return key


def resolve_claim_by_key(db: Session, api_key: str) -> Optional[VenueClaim]:
    """Find the verified, currently-active claim owning this API key (if any)."""
    if not api_key or not api_key.startswith("vk_"):
        return None
    q = (
        db.query(VenueClaim)
        .filter(VenueClaim.status == "verified")
        .order_by(desc(VenueClaim.verified_at))
    )
    for claim in q.limit(500).all():
        if (claim.meta or {}).get("api_key") != api_key:
            continue
        # Inactive (expired) claims behave as if the key was revoked.
        if not is_ownership_active(claim):
            continue
        return claim
    return None


def owned_claims_for(db: Session, claim: VenueClaim) -> list[VenueClaim]:
    """Return every claim (verified OR needs_reverify) held by the same owner email.
    needs_reverify rows are included so the UI can surface the lock-out banner."""
    return (
        db.query(VenueClaim)
        .filter(
            VenueClaim.email == claim.email,
            VenueClaim.status.in_(("verified", "needs_reverify")),
        )
        .order_by(desc(VenueClaim.verified_at))
        .all()
    )


def claim_for_venue_owned_by(db: Session, authed: VenueClaim, venue_id: str) -> Optional[VenueClaim]:
    """Find the verified claim for `venue_id` that belongs to the same owner-email
    as the authed claim. Used by endpoints that accept a venue_id path param."""
    return (
        db.query(VenueClaim)
        .filter(
            VenueClaim.email == authed.email,
            VenueClaim.venue_id == venue_id,
            VenueClaim.status == "verified",
        )
        .order_by(desc(VenueClaim.verified_at))
        .first()
    )


# ---------------------------------------------------------------------------
# Venue data for the owner
# ---------------------------------------------------------------------------
def owner_summary(db: Session, claim: VenueClaim) -> dict:
    """Return owner details + all venues they own (verified claims same email)."""
    owned = owned_claims_for(db, claim)
    # Ensure the authed claim is always first (stable UX after refresh).
    owned.sort(key=lambda c: (c.id != claim.id, -(c.verified_at.timestamp() if c.verified_at else 0)))

    venues_out: list[dict] = []
    for oc in owned:
        venue = db.get(Venue, oc.venue_id)
        if not venue:
            continue
        vibe = db.get(Vibe, venue.id)
        sig = db.query(VenueSignals).filter(VenueSignals.venue_id == venue.id).one_or_none()
        profile = db.get(VenueProfile, venue.id)
        tags = (profile.tags if profile else None) or {}
        handles = tags.get("social_handles") or {}
        hooks = (oc.meta or {}).get("webhooks") or {}
        active = is_ownership_active(oc)
        exp_raw = (oc.meta or {}).get("ownership_expires_at")
        venues_out.append({
            "id": venue.id,
            "name": venue.name,
            "category": venue.category.value if hasattr(venue.category, "value") else venue.category,
            "lat": venue.latitude,
            "lng": venue.longitude,
            "is_verified": active,
            "ownership_active": active,
            "ownership_expires_at": exp_raw,
            "transfer_requested": bool((oc.meta or {}).get("transfer_requested")),
            "transfer_email": (oc.meta or {}).get("transfer_email"),
            "status": oc.status,
            "vibe_score": float(vibe.vibe_score) if vibe else 0.0,
            "crowd_level": (
                vibe.crowd_level.value if vibe and hasattr(vibe.crowd_level, "value")
                else (vibe.crowd_level if vibe else None)
            ),
            "last_updated": vibe.last_updated.isoformat() if vibe and vibe.last_updated else None,
            "external_signals": sig.as_dict() if sig else None,
            "social_handles": handles,
            "webhooks": {
                "slack_webhook_url": hooks.get("slack_webhook_url") or "",
                "discord_webhook_url": hooks.get("discord_webhook_url") or "",
            },
            "claim_id": oc.id,
        })

    return {
        "owner": {
            "email": claim.email,
            "name": claim.owner_name,
            "claim_id": claim.id,
            "verified_at": claim.verified_at.isoformat() if claim.verified_at else None,
            "venue_count": len(venues_out),
        },
        "venues": venues_out,
    }


def set_social_handles(
    db: Session, claim: VenueClaim, *, instagram: Optional[str], tiktok: Optional[str],
    venue_id: Optional[str] = None,
) -> dict:
    """Set handles on the owner's venue. If `venue_id` is omitted, fall back to
    the authed claim's venue (single-venue legacy path)."""
    target_venue_id = venue_id or claim.venue_id
    # Cross-venue auth: ensure the authed owner actually owns `target_venue_id`.
    if target_venue_id != claim.venue_id:
        if not claim_for_venue_owned_by(db, claim, target_venue_id):
            raise PermissionError("venue not owned by this owner")
    venue = db.get(Venue, target_venue_id)
    if not venue:
        raise ValueError("venue not found")
    profile = db.get(VenueProfile, venue.id)
    if profile is None:
        profile = VenueProfile(venue_id=venue.id)
        db.add(profile)

    tags = dict(profile.tags or {})
    handles = dict(tags.get("social_handles") or {})
    # Strip leading '@' and whitespace; empty string clears the handle.
    if instagram is not None:
        val = (instagram or "").strip().lstrip("@")
        if val:
            handles["instagram"] = val
        else:
            handles.pop("instagram", None)
    if tiktok is not None:
        val = (tiktok or "").strip().lstrip("@")
        if val:
            handles["tiktok"] = val
        else:
            handles.pop("tiktok", None)
    tags["social_handles"] = handles
    profile.tags = tags
    profile.updated_at = datetime.now(timezone.utc)
    db.commit()
    return handles


# ---------------------------------------------------------------------------
# Owner-scoped webhook subscriptions
# ---------------------------------------------------------------------------
SLACK_PREFIX = "https://hooks.slack.com/"
DISCORD_PREFIX = "https://discord.com/api/webhooks/"


def _validate_webhook_url(kind: str, url: str) -> Optional[str]:
    if not url:
        return None  # empty → clear
    if kind == "slack" and not url.startswith(SLACK_PREFIX):
        raise ValueError(f"slack_webhook_url must start with {SLACK_PREFIX}")
    if kind == "discord" and not url.startswith(DISCORD_PREFIX):
        raise ValueError(f"discord_webhook_url must start with {DISCORD_PREFIX}")
    return url


def set_venue_webhooks(
    db: Session, authed: VenueClaim, *, venue_id: str,
    slack_webhook_url: Optional[str] = None,
    discord_webhook_url: Optional[str] = None,
) -> dict:
    """Store per-venue webhook URLs on the owning claim's meta.webhooks."""
    target = (
        authed if venue_id == authed.venue_id
        else claim_for_venue_owned_by(db, authed, venue_id)
    )
    if not target:
        raise PermissionError("venue not owned by this owner")

    meta = dict(target.meta or {})
    hooks = dict(meta.get("webhooks") or {})
    if slack_webhook_url is not None:
        v = _validate_webhook_url("slack", (slack_webhook_url or "").strip())
        if v:
            hooks["slack_webhook_url"] = v
        else:
            hooks.pop("slack_webhook_url", None)
    if discord_webhook_url is not None:
        v = _validate_webhook_url("discord", (discord_webhook_url or "").strip())
        if v:
            hooks["discord_webhook_url"] = v
        else:
            hooks.pop("discord_webhook_url", None)
    meta["webhooks"] = hooks
    target.meta = meta
    db.commit()
    return {
        "venue_id": venue_id,
        "webhooks": {
            "slack_webhook_url": hooks.get("slack_webhook_url") or "",
            "discord_webhook_url": hooks.get("discord_webhook_url") or "",
        },
    }


def get_venue_webhook_urls(db: Session, venue_id: str) -> list[tuple[str, str]]:
    """Return [(kind, url), ...] for all owner-configured webhooks on a venue."""
    claims = (
        db.query(VenueClaim)
        .filter(VenueClaim.venue_id == venue_id, VenueClaim.status == "verified")
        .all()
    )
    out: list[tuple[str, str]] = []
    for c in claims:
        hooks = (c.meta or {}).get("webhooks") or {}
        slack = (hooks.get("slack_webhook_url") or "").strip()
        discord = (hooks.get("discord_webhook_url") or "").strip()
        if slack:
            out.append(("slack", slack))
        if discord:
            out.append(("discord", discord))
    return out


def owner_inbox(db: Session, claim: VenueClaim, limit: int = 20) -> list[dict]:
    """Return inbox items for this owner (claim-scoped)."""
    rows = (
        db.query(NotificationLog)
        .filter(NotificationLog.wallet_id == f"owner:{claim.id}")
        .order_by(desc(NotificationLog.created_at))
        .limit(limit)
        .all()
    )
    return [{
        "id": r.id, "kind": r.kind, "title": r.title, "body": r.body,
        "data": r.data or {}, "created_at": r.created_at.isoformat(),
    } for r in rows]


def seed_welcome_inbox(db: Session, claim: VenueClaim) -> Optional[NotificationLog]:
    """Drop a "Welcome, owner" message into the owner's scoped inbox. Idempotent."""
    wallet_id = f"owner:{claim.id}"
    existing = (
        db.query(NotificationLog)
        .filter(NotificationLog.wallet_id == wallet_id, NotificationLog.kind == "welcome_owner")
        .first()
    )
    if existing:
        return existing

    import uuid
    venue = db.get(Venue, claim.venue_id)
    row = NotificationLog(
        id=str(uuid.uuid4()),
        wallet_id=wallet_id,
        kind="welcome_owner",
        title="Welcome, owner ✨",
        body=(
            f"You're now verified as the owner of {venue.name if venue else claim.venue_id}. "
            "Tap to open your private dashboard."
        ),
        data={
            "venue_id": claim.venue_id,
            "venue_name": venue.name if venue else None,
            "claim_id": claim.id,
            "deep_link": f"/owner?claim={claim.id}",
        },
    )
    db.add(row)
    db.commit()
    return row


def maybe_send_welcome_push(db: Session, claim: VenueClaim) -> dict:
    """If a UserPushToken exists for `wallet_id == claim.email` we send a push.
    Otherwise we silently skip (the inbox entry is still there to pick up later).
    """
    from app.services.notifications import get_token, send_push
    wallet_id = claim.email  # owners may later link their wallet to their email
    if not get_token(db, wallet_id):
        return {"ok": False, "skipped": "no_push_token_for_email"}

    venue = db.get(Venue, claim.venue_id)
    return send_push(
        db, wallet_id=wallet_id,
        title="Welcome, owner ✨",
        body=f"You're now verified as the owner of {venue.name if venue else claim.venue_id}.",
        data={
            "kind": "welcome_owner",
            "venue_id": claim.venue_id,
            "claim_id": claim.id,
            "deep_link": f"/owner?claim={claim.id}",
        },
    )

# ---------------------------------------------------------------------------
# Transfer / expire / re-verify (Iter 16)
# ---------------------------------------------------------------------------
from datetime import timedelta

TRANSFER_TTL_MIN = 60


async def request_transfer(
    db: Session, authed: VenueClaim, *, venue_id: str, new_email: str,
    base_url_fallback: str,
) -> dict:
    """Mark a transfer intent on the claim and email the new owner a magic link."""
    target = (
        authed if venue_id == authed.venue_id
        else claim_for_venue_owned_by(db, authed, venue_id)
    )
    if not target:
        raise PermissionError("venue not owned by this owner")
    if not is_ownership_active(target):
        raise ValueError("ownership is not active")

    token = "tr_" + secrets.token_urlsafe(24)
    expires = datetime.now(timezone.utc) + timedelta(minutes=TRANSFER_TTL_MIN)

    meta = dict(target.meta or {})
    meta["transfer_requested"] = True
    meta["transfer_email"] = new_email.strip().lower()
    meta["transfer_token"] = token
    meta["transfer_expires_at"] = expires.isoformat()
    target.meta = meta
    db.commit()

    from app.services.email import send_email, is_configured as email_configured
    import os as _os
    base = (
        _os.environ.get("CLAIM_LINK_BASE_URL", "").strip().rstrip("/")
        or base_url_fallback.rstrip("/")
    )
    link = f"{base}/api/owner/transfer/accept/{token}"
    venue = db.get(Venue, venue_id)
    subject = f"Ownership transfer requested for {venue.name if venue else venue_id}"
    html = (
        f"<p>Hi,</p>"
        f"<p>{target.owner_name} has requested to transfer ownership of "
        f"<strong>{venue.name if venue else venue_id}</strong> on Vibe2Nite to you.</p>"
        f"<p><a href='{link}'>Accept the transfer</a> "
        f"(single-use, expires in {TRANSFER_TTL_MIN} minutes).</p>"
        f"<p>If you didn't expect this, simply ignore this email.</p>"
    )
    text = (
        f"{target.owner_name} requested to transfer ownership of "
        f"{venue.name if venue else venue_id}. Accept here: {link}"
    )
    mail_status = await send_email(to=new_email, subject=subject, html=html, text=text)

    return {
        "claim_id": target.id,
        "transfer_requested": True,
        "transfer_email": new_email,
        "email_provider_live": email_configured(),
        "email_delivery": mail_status,
        "magic_link": link if not mail_status.get("sent") else None,
        "expires_at": expires.isoformat(),
    }


def accept_transfer(db: Session, token: str) -> dict:
    now = datetime.now(timezone.utc)
    candidates = (
        db.query(VenueClaim)
        .filter(VenueClaim.status == "verified")
        .all()
    )
    target: Optional[VenueClaim] = None
    for c in candidates:
        if (c.meta or {}).get("transfer_token") == token:
            target = c
            break
    if not target:
        return {"ok": False, "reason": "invalid_token"}

    raw_exp = (target.meta or {}).get("transfer_expires_at")
    try:
        exp = datetime.fromisoformat(raw_exp) if raw_exp else None
    except Exception:
        exp = None
    if not exp or exp <= now:
        meta = dict(target.meta or {})
        for k in ("transfer_token", "transfer_expires_at"):
            meta.pop(k, None)
        target.meta = meta
        db.commit()
        return {"ok": False, "reason": "expired"}

    new_email = (target.meta or {}).get("transfer_email")
    if not new_email:
        return {"ok": False, "reason": "no_transfer_email"}

    old_meta = dict(target.meta or {})
    target.status = "rejected"
    target.meta = {**old_meta, "transferred_to": new_email,
                   "transfer_accepted_at": now.isoformat(),
                   "api_key": None,
                   "transfer_requested": False,
                   "transfer_token": None,
                   "transfer_expires_at": None}
    db.commit()

    import uuid as _uuid
    new_claim = VenueClaim(
        id=str(_uuid.uuid4()),
        venue_id=target.venue_id,
        owner_name=new_email.split("@")[0],
        email=new_email,
        proof=f"transfer from {target.email}",
        status="verified",
        verified_at=now,
        meta={"transferred_from": target.email, "transferred_from_claim": target.id},
    )
    db.add(new_claim)
    db.commit()
    db.refresh(new_claim)

    new_key = mint_api_key(db, new_claim)
    seed_welcome_inbox(db, new_claim)
    try:
        maybe_send_welcome_push(db, new_claim)
    except Exception:
        pass

    try:
        from app.services import webhooks as wh
        venue = db.get(Venue, target.venue_id)
        wh.dispatch(
            "VENUE_CLAIMED",
            title=f"{venue.name if venue else target.venue_id} transferred",
            body=f"Ownership transferred from {target.email} to {new_email}.",
            meta={
                "venue_id": target.venue_id,
                "venue_name": venue.name if venue else None,
                "new_owner_email": new_email,
                "previous_owner_email": target.email,
                "claim_id": new_claim.id,
                "transfer": True,
            },
        )
    except Exception:
        pass

    return {
        "ok": True,
        "venue_id": target.venue_id,
        "new_owner_email": new_email,
        "owner_api_key": new_key,
    }


def admin_expire_ownership(db: Session, venue_id: str, reviewer: str = "admin") -> dict:
    now = datetime.now(timezone.utc)
    claims = (
        db.query(VenueClaim)
        .filter(VenueClaim.venue_id == venue_id, VenueClaim.status == "verified")
        .all()
    )
    if not claims:
        return {"ok": False, "reason": "no_active_ownership", "affected": 0}
    for c in claims:
        meta = dict(c.meta or {})
        meta["ownership_expires_at"] = now.isoformat()
        meta.pop("api_key", None)
        meta["expired_by"] = reviewer
        c.meta = meta
        c.status = "needs_reverify"
    db.commit()

    try:
        from app.services import webhooks as wh
        venue = db.get(Venue, venue_id)
        wh.dispatch(
            "VENUE_CLOSED",
            title=f"{venue.name if venue else venue_id} ownership expired",
            body=f"Admin {reviewer} expired ownership. Re-verification required.",
            meta={"venue_id": venue_id, "expired_by": reviewer, "kind": "ownership_expired"},
        )
    except Exception:
        pass

    return {"ok": True, "venue_id": venue_id, "affected": len(claims)}

