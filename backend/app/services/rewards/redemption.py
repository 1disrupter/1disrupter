# -*- coding: utf-8 -*-
"""Redemption — spend credits on a venue offer and record a ledger row."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import VenueRedemption, VenueRewardOffer
from app.services.rewards.credit_wallet import deduct_credits


class RedemptionError(Exception):
    pass


def redeem(db: Session, *, user_id: str, offer_id: str) -> VenueRedemption:
    offer = db.get(VenueRewardOffer, offer_id)
    if offer is None or not offer.active:
        raise RedemptionError("offer not available")

    try:
        deduct_credits(db, user_id, offer.cost_credits)
    except ValueError as exc:
        raise RedemptionError(str(exc)) from exc

    row = VenueRedemption(
        user_id=user_id,
        venue_id=offer.venue_id,
        offer_id=offer.id,
        cost_credits=offer.cost_credits,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_redemptions(
    db: Session, *, venue_id: Optional[str] = None, user_id: Optional[str] = None,
    limit: int = 100,
) -> List[VenueRedemption]:
    q = db.query(VenueRedemption)
    if venue_id:
        q = q.filter(VenueRedemption.venue_id == venue_id)
    if user_id:
        q = q.filter(VenueRedemption.user_id == user_id)
    return q.order_by(VenueRedemption.timestamp.desc()).limit(limit).all()
