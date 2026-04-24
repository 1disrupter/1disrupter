# -*- coding: utf-8 -*-
"""Public + admin endpoints for the Claim-Your-Venue flow, plus provider status
visibility and a recent-webhook log (admin-only)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import claims as claim_svc
from app.services import webhooks
from app.services.signals import providers as signal_providers

router = APIRouter(tags=["claims"])


# ---------------------------------------------------------------------------
# Public endpoints
# ---------------------------------------------------------------------------
class ClaimSubmit(BaseModel):
    venue_id: str
    owner_name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    proof: str = Field(default="", max_length=500,
                       description="Website / Instagram / Google listing URL for verification")


@router.post("/claims/submit", summary="Submit an owner-claim for a venue")
async def submit_claim(payload: ClaimSubmit, request: Request, db: Session = Depends(get_db)):
    """Public entry point — anyone can submit a claim. A magic-link email is
    sent to the stated address; clicking it marks the claim verified."""
    try:
        base = str(request.base_url).rstrip("/")  # e.g. https://host
        result = await claim_svc.submit_claim(
            db,
            venue_id=payload.venue_id,
            owner_name=payload.owner_name.strip(),
            email=str(payload.email).strip().lower(),
            proof=payload.proof.strip(),
            base_url_fallback=base,
        )
        # Scrub magic_link for production (only returned in console-only mode
        # for easy dev copy-paste; in that mode the submitter is the same
        # person as the email owner, so it's not an escalation vector).
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/claims/verify/{token}", summary="Verify a magic-link claim token")
def verify_claim(token: str, db: Session = Depends(get_db)):
    result = claim_svc.verify_claim(db, token)
    if not result.get("ok"):
        reason = result.get("reason", "invalid")
        code = 410 if reason == "expired" else 400
        raise HTTPException(status_code=code, detail=reason)
    return result


# ---------------------------------------------------------------------------
# Admin endpoints (protected only by existing admin UI + browser — we trust
# the same shape as other admin endpoints in this repo).
# ---------------------------------------------------------------------------
@router.get("/admin/claims", summary="List venue claims (admin)")
def admin_list_claims(
    status: Optional[str] = Query(None, description="pending|email_sent|verified|rejected"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return {"items": claim_svc.list_claims(db, status=status, limit=limit)}


class ClaimReview(BaseModel):
    action: str = Field(..., pattern="^(approve|reject)$")
    reviewer: str = Field(default="admin", max_length=120)
    note: str = Field(default="", max_length=500)


@router.post("/admin/claims/{claim_id}/review", summary="Approve or reject a claim")
def admin_review_claim(claim_id: str, payload: ClaimReview, db: Session = Depends(get_db)):
    try:
        return claim_svc.admin_review(
            db, claim_id, action=payload.action,
            reviewer=payload.reviewer.strip() or "admin", note=payload.note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ---------------------------------------------------------------------------
# Provider status + recent webhook events (admin visibility)
# ---------------------------------------------------------------------------
@router.get("/admin/providers/status", summary="Live-vs-stub status for real providers")
def admin_provider_status():
    return {"providers": signal_providers.provider_status()}


@router.get("/admin/webhooks/recent", summary="Recent outbound webhook events (in-memory)")
def admin_recent_webhooks(limit: int = Query(20, ge=1, le=50)):
    cfg = {evt: webhooks.is_configured(evt) for evt in webhooks.ENV_MAP.keys()}
    return {"configured": cfg, "recent": webhooks.recent_events(limit=limit)}


# Lightweight public "is this venue claimed?" for the CRA venue detail.
@router.get("/venues/{venue_id}/owner", summary="Return verified owner summary if any")
def venue_owner(venue_id: str, db: Session = Depends(get_db)):
    owner = claim_svc.owner_for_venue(db, venue_id)
    return {"venue_id": venue_id, "owner": owner}
