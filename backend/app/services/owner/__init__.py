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
# Key lifecycle
# ---------------------------------------------------------------------------
def mint_api_key(db: Session, claim: VenueClaim) -> str:
    """Generate + persist an owner API key into the claim meta (idempotent)."""
    meta = dict(claim.meta or {})
    key = meta.get("api_key")
    if not key:
        key = "vk_" + secrets.token_urlsafe(28)
        meta["api_key"] = key
        claim.meta = meta
        db.commit()
    return key


def resolve_claim_by_key(db: Session, api_key: str) -> Optional[VenueClaim]:
    """Find the verified claim owning this API key (if any)."""
    if not api_key or not api_key.startswith("vk_"):
        return None
    # JSON query — portable subset: scan verified claims. Volume is tiny.
    q = (
        db.query(VenueClaim)
        .filter(VenueClaim.status == "verified")
        .order_by(desc(VenueClaim.verified_at))
    )
    for claim in q.limit(500).all():
        if (claim.meta or {}).get("api_key") == api_key:
            return claim
    return None


# ---------------------------------------------------------------------------
# Venue data for the owner
# ---------------------------------------------------------------------------
def owner_summary(db: Session, claim: VenueClaim) -> dict:
    venue = db.get(Venue, claim.venue_id)
    if not venue:
        return {"owner": {"email": claim.email, "name": claim.owner_name}, "venues": []}

    vibe = db.get(Vibe, venue.id)
    sig = db.query(VenueSignals).filter(VenueSignals.venue_id == venue.id).one_or_none()
    profile = db.get(VenueProfile, venue.id)

    handles = {}
    if profile and profile.tags:
        handles = (profile.tags or {}).get("social_handles") or {}

    return {
        "owner": {
            "email": claim.email,
            "name": claim.owner_name,
            "claim_id": claim.id,
            "verified_at": claim.verified_at.isoformat() if claim.verified_at else None,
        },
        "venues": [{
            "id": venue.id,
            "name": venue.name,
            "category": venue.category.value if hasattr(venue.category, "value") else venue.category,
            "lat": venue.latitude,
            "lng": venue.longitude,
            "vibe_score": float(vibe.vibe_score) if vibe else 0.0,
            "crowd_level": (
                vibe.crowd_level.value if vibe and hasattr(vibe.crowd_level, "value")
                else (vibe.crowd_level if vibe else None)
            ),
            "last_updated": vibe.last_updated.isoformat() if vibe and vibe.last_updated else None,
            "external_signals": sig.as_dict() if sig else None,
            "social_handles": handles,
        }],
    }


def set_social_handles(
    db: Session, claim: VenueClaim, *, instagram: Optional[str], tiktok: Optional[str],
) -> dict:
    venue = db.get(Venue, claim.venue_id)
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
