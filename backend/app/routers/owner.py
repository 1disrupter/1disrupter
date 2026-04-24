# -*- coding: utf-8 -*-
"""Owner-scoped endpoints (auth: X-Owner-Key header)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import owner as owner_svc
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


@router.get("/me", summary="Return the owner dashboard summary")
def me(claim: VenueClaim = Depends(_auth), db: Session = Depends(get_db)):
    return owner_svc.owner_summary(db, claim)


@router.get("/inbox", summary="Return the owner's inbox (welcome messages, etc.)")
def inbox(limit: int = 20, claim: VenueClaim = Depends(_auth), db: Session = Depends(get_db)):
    return {"items": owner_svc.owner_inbox(db, claim, limit=limit)}


class HandlesIn(BaseModel):
    instagram: Optional[str] = Field(None, max_length=120)
    tiktok: Optional[str] = Field(None, max_length=120)


@router.put("/venue/handles", summary="Set this venue's social handles (used by real providers)")
def set_handles(
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
