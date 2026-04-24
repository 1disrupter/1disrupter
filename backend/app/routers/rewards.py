# -*- coding: utf-8 -*-
"""Vibe Credits Reward Economy routes."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Venue
from app.services.rewards import (
    add_credits,
    create_offer,
    credits_for,
    deactivate_offer,
    get_offer,
    get_wallet,
    list_offers,
    list_redemptions,
    list_rules,
    redeem,
)
from app.services.rewards.redemption import RedemptionError
from app.services.notifications import milestone_for, send_milestone_push

router = APIRouter(prefix="/rewards", tags=["rewards"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class WalletOut(BaseModel):
    user_id: str
    credits: int
    updated_at: datetime


class EarnIn(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=120)
    action: str = Field(..., min_length=1, max_length=64)
    amount: Optional[int] = Field(None, ge=1, le=1000)


class EarnOut(BaseModel):
    user_id: str
    action: str
    awarded: int
    credits: int


class OfferIn(BaseModel):
    venue_id: str
    name: str = Field(..., min_length=1, max_length=120)
    cost_credits: int = Field(..., ge=1, le=100000)
    description: Optional[str] = ""
    active: bool = True


class OfferOut(BaseModel):
    id: str
    venue_id: str
    name: str
    description: str
    cost_credits: int
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RedeemIn(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=120)
    offer_id: str


class RedemptionOut(BaseModel):
    id: str
    user_id: str
    venue_id: str
    offer_id: str
    cost_credits: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Wallet + earn
# ---------------------------------------------------------------------------
@router.get("/rules", summary="List canonical reward rules")
def rules():
    return list_rules()


@router.get("/wallet/{user_id}", response_model=WalletOut, summary="Get a user wallet balance")
def wallet(
    user_id: str,
    create: bool = Query(True, description="Auto-create an empty wallet if missing"),
    db: Session = Depends(get_db),
) -> WalletOut:
    """Return wallet for `user_id`. If `create=false`, return 404 when absent
    (use this for "restore wallet" flows — prevents typos from silently
    spawning empty wallets)."""
    if not create:
        from app.models import UserWallet
        w = db.get(UserWallet, user_id)
        if w is None:
            raise HTTPException(status_code=404, detail="wallet not found")
        return WalletOut(user_id=w.user_id, credits=w.credits, updated_at=w.updated_at)
    w = get_wallet(db, user_id)
    return WalletOut(user_id=w.user_id, credits=w.credits, updated_at=w.updated_at)


@router.post("/earn", response_model=EarnOut, summary="Award credits to a user for an action")
def earn(payload: EarnIn, db: Session = Depends(get_db)) -> EarnOut:
    award = int(payload.amount) if payload.amount is not None else credits_for(payload.action)
    if award <= 0:
        raise HTTPException(status_code=400, detail="unknown action / no credits configured")

    # Capture the previous balance so we can detect milestone crossings.
    prev_wallet = get_wallet(db, payload.user_id)
    previous = int(prev_wallet.credits or 0)

    w = add_credits(db, payload.user_id, award)

    # Fire-and-forget milestone push. Never raise into the route.
    crossed = milestone_for(previous, int(w.credits or 0))
    if crossed is not None:
        try:
            send_milestone_push(db, wallet_id=payload.user_id, milestone=crossed, total=int(w.credits or 0))
        except Exception:  # pragma: no cover
            pass

    # Action-specific pushes (daily_login, first_visit_bonus) — additive.
    try:
        if payload.action == "daily_login":
            from app.services.notifications.push_engine import send_daily_login
            send_daily_login(db, payload.user_id)
        elif payload.action == "first_visit_bonus":
            from app.services.notifications.push_engine import send_first_visit
            send_first_visit(db, payload.user_id, "")
    except Exception:  # pragma: no cover
        pass

    return EarnOut(
        user_id=w.user_id, action=payload.action, awarded=award, credits=w.credits,
    )


# ---------------------------------------------------------------------------
# Offers
# ---------------------------------------------------------------------------
@router.get("/offers", response_model=List[OfferOut], summary="List reward offers")
def get_offers(
    venue_id: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    return [OfferOut.model_validate(o) for o in list_offers(db, venue_id=venue_id, active_only=active_only)]


@router.get("/offers/{offer_id}", response_model=OfferOut, summary="Fetch a single offer")
def get_one_offer(offer_id: str, db: Session = Depends(get_db)):
    o = get_offer(db, offer_id)
    if o is None:
        raise HTTPException(status_code=404, detail="offer not found")
    return OfferOut.model_validate(o)


@router.post("/offers", response_model=OfferOut, status_code=201, summary="Create a reward offer (admin)")
def create_new_offer(payload: OfferIn, db: Session = Depends(get_db)):
    venue = db.get(Venue, payload.venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="venue not found")
    row = create_offer(
        db, venue_id=payload.venue_id, name=payload.name, cost_credits=payload.cost_credits,
        description=payload.description or "", active=payload.active,
    )
    # Fire offer_drop push to every registered wallet. Best-effort.
    try:
        from app.services.notifications.push_engine import broadcast_to_all, send_offer_drop
        broadcast_to_all(
            db, send_fn=send_offer_drop, venue=venue,
            offer_name=row.name, cost=int(row.cost_credits), offer_id=row.id,
        )
    except Exception:  # pragma: no cover
        pass
    return OfferOut.model_validate(row)


@router.delete("/offers/{offer_id}", response_model=OfferOut, summary="Deactivate a reward offer (admin)")
def remove_offer(offer_id: str, db: Session = Depends(get_db)):
    row = deactivate_offer(db, offer_id)
    if row is None:
        raise HTTPException(status_code=404, detail="offer not found")
    return OfferOut.model_validate(row)


# ---------------------------------------------------------------------------
# Redemption
# ---------------------------------------------------------------------------
@router.post("/redeem", response_model=RedemptionOut, summary="Redeem an offer with credits")
def redeem_offer(payload: RedeemIn, db: Session = Depends(get_db)):
    try:
        row = redeem(db, user_id=payload.user_id, offer_id=payload.offer_id)
    except RedemptionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return RedemptionOut.model_validate(row)


@router.get("/redemptions", response_model=List[RedemptionOut], summary="List recent redemptions")
def get_redemptions(
    venue_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return [
        RedemptionOut.model_validate(r)
        for r in list_redemptions(db, venue_id=venue_id, user_id=user_id, limit=limit)
    ]
