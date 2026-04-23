# -*- coding: utf-8 -*-
"""Venue reward offers — admin-managed catalogue of things to spend credits on."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import VenueRewardOffer


def create_offer(
    db: Session, *, venue_id: str, name: str, cost_credits: int,
    description: str = "", active: bool = True,
) -> VenueRewardOffer:
    row = VenueRewardOffer(
        venue_id=venue_id,
        name=name,
        description=description or "",
        cost_credits=int(cost_credits),
        active=bool(active),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_offers(
    db: Session, venue_id: Optional[str] = None, active_only: bool = True,
) -> List[VenueRewardOffer]:
    q = db.query(VenueRewardOffer)
    if venue_id:
        q = q.filter(VenueRewardOffer.venue_id == venue_id)
    if active_only:
        q = q.filter(VenueRewardOffer.active.is_(True))
    return q.order_by(VenueRewardOffer.cost_credits.asc()).all()


def get_offer(db: Session, offer_id: str) -> Optional[VenueRewardOffer]:
    return db.get(VenueRewardOffer, offer_id)


def deactivate_offer(db: Session, offer_id: str) -> Optional[VenueRewardOffer]:
    row = db.get(VenueRewardOffer, offer_id)
    if row is None:
        return None
    row.active = False
    db.commit()
    db.refresh(row)
    return row
