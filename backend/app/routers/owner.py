# -*- coding: utf-8 -*-
"""Owner-scoped endpoints (auth: X-Owner-Key header)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import owner as owner_svc
from app.services import webhooks as wh_svc
from app.models import VenueClaim

router = APIRouter(prefix="/owner", tags=["owner"])


def _auth(
    x_owner_key: Optional[str] = Header(None, convert_underscores=False, alias="X-Owner-Key"),
    db: Session = Depends(get_db),
) -> VenueClaim:
    if not x_owner_key:
        raise HTTPException(status_code=401, detail="missing X-Owner-Key header")
    claim = owner_svc.resolve_claim_by_key(db, x_owner_key)
    if not claim:
        raise HTTPException(status_code=401, detail="invalid or expired owner key")
    return claim


@router.get("/me", summary="Return the owner dashboard summary (all owned venues)")
def me(claim: VenueClaim = Depends(_auth), db: Session = Depends(get_db)):
    return owner_svc.owner_summary(db, claim)


@router.get("/venues", summary="Return every venue owned by the authed owner")
def venues(claim: VenueClaim = Depends(_auth), db: Session = Depends(get_db)):
    summary = owner_svc.owner_summary(db, claim)
    # Compact shape tailored for the venue-switcher.
    return {
        "count": len(summary["venues"]),
        "items": [{
            "id": v["id"],
            "name": v["name"],
            "category": v["category"],
            "is_verified": v.get("is_verified", True),
            "vibe_score": v.get("vibe_score", 0.0),
            "crowd_level": v.get("crowd_level"),
            "external_signals": v.get("external_signals"),
        } for v in summary["venues"]],
    }


@router.get("/inbox", summary="Return the owner's inbox (welcome messages, etc.)")
def inbox(limit: int = 20, claim: VenueClaim = Depends(_auth), db: Session = Depends(get_db)):
    return {"items": owner_svc.owner_inbox(db, claim, limit=limit)}


class HandlesIn(BaseModel):
    instagram: Optional[str] = Field(None, max_length=120)
    tiktok: Optional[str] = Field(None, max_length=120)


@router.put("/venue/handles", summary="Set the authed claim's venue handles (legacy single-venue path)")
def set_handles_legacy(
    payload: HandlesIn,
    claim: VenueClaim = Depends(_auth),
    db: Session = Depends(get_db),
):
    try:
        handles = owner_svc.set_social_handles(
            db, claim, instagram=payload.instagram, tiktok=payload.tiktok,
        )
        return {"venue_id": claim.venue_id, "social_handles": handles}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.put("/venue/{venue_id}/handles", summary="Set social handles for one of the owned venues")
def set_handles(
    venue_id: str,
    payload: HandlesIn,
    claim: VenueClaim = Depends(_auth),
    db: Session = Depends(get_db),
):
    try:
        handles = owner_svc.set_social_handles(
            db, claim, instagram=payload.instagram, tiktok=payload.tiktok, venue_id=venue_id,
        )
        return {"venue_id": venue_id, "social_handles": handles}
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


class WebhooksIn(BaseModel):
    slack_webhook_url: Optional[str] = Field(None, max_length=500)
    discord_webhook_url: Optional[str] = Field(None, max_length=500)


# ---------------------------------------------------------------------------
# Iter 16 — Ownership transfer + re-verify
# ---------------------------------------------------------------------------
class TransferRequestIn(BaseModel):
    email: str = Field(..., min_length=3, max_length=200)


@router.post("/venue/{venue_id}/transfer/request", summary="Start an ownership transfer")
async def transfer_request(
    venue_id: str,
    payload: TransferRequestIn,
    request: Request,
    claim: VenueClaim = Depends(_auth),
    db: Session = Depends(get_db),
):
    try:
        return await owner_svc.request_transfer(
            db, claim, venue_id=venue_id,
            new_email=payload.email,
            base_url_fallback=str(request.base_url).rstrip("/"),
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/transfer/accept/{token}", summary="Accept a pending ownership transfer (magic link)")
@router.post("/transfer/accept/{token}", summary="Accept a pending ownership transfer (magic link)")
def transfer_accept(token: str, db: Session = Depends(get_db)):
    result = owner_svc.accept_transfer(db, token)
    if not result.get("ok"):
        reason = result.get("reason", "invalid")
        code = 410 if reason == "expired" else 400
        raise HTTPException(status_code=code, detail=reason)
    return result


@router.put("/venue/{venue_id}/webhooks", summary="Set owner-triggered webhook URLs for a venue")
def set_webhooks(
    venue_id: str,
    payload: WebhooksIn,
    claim: VenueClaim = Depends(_auth),
    db: Session = Depends(get_db),
):
    try:
        return owner_svc.set_venue_webhooks(
            db, claim, venue_id=venue_id,
            slack_webhook_url=payload.slack_webhook_url,
            discord_webhook_url=payload.discord_webhook_url,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/venue/{venue_id}/webhooks/test", summary="Fire a test webhook to the owner's configured URLs")
def test_webhook(
    venue_id: str,
    claim: VenueClaim = Depends(_auth),
    db: Session = Depends(get_db),
):
    # Cross-venue auth gate.
    target = (
        claim if venue_id == claim.venue_id
        else owner_svc.claim_for_venue_owned_by(db, claim, venue_id)
    )
    if not target:
        raise HTTPException(status_code=403, detail="venue not owned by this owner")
    hooks = owner_svc.get_venue_webhook_urls(db, venue_id)
    if not hooks:
        raise HTTPException(status_code=400, detail="no owner webhooks configured for this venue")

    from app.models import Venue
    venue = db.get(Venue, venue_id)
    wh_svc.dispatch_owner(
        "OWNER_TEST",
        venue_id=venue_id,
        title=f"Test webhook · {venue.name if venue else venue_id}",
        body="If you're seeing this in your channel, your owner webhook is wired up ✅",
        meta={"venue_id": venue_id, "test": True},
    )
    return {"sent": True, "targets": [{"kind": k, "url_prefix": u.split('/')[2]} for k, u in hooks]}
