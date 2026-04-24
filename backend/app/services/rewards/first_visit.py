# -*- coding: utf-8 -*-
"""First-verified-visit reward loop.

When a user visits a verified venue (by VenueVisit record), they become eligible
for a +15 vibe-credit bonus once per (venue, UTC day). The helper is idempotent:
calling it twice for the same (venue, user, day) returns the same result without
double-crediting.
"""
from __future__ import annotations

import logging
from datetime import datetime, time, timezone
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models import UserWallet, Venue, VenueVisit
from app.services.rewards.credit_wallet import add_credits
from app.services.venues.ownership import verified_venue_ids

logger = logging.getLogger("vibe2nite.rewards.first_visit")

FIRST_VISIT_BONUS = 15


def _utc_day_bounds(moment: datetime) -> tuple[datetime, datetime]:
    d = moment.astimezone(timezone.utc).date()
    start = datetime.combine(d, time.min, tzinfo=timezone.utc)
    end = datetime.combine(d, time.max, tzinfo=timezone.utc)
    return start, end


def get_first_visit_for_venue_today(
    db: Session, venue_id: str, at: Optional[datetime] = None,
) -> Optional[str]:
    """Return the `device_id` of the first visitor for this venue on the UTC
    calendar day containing `at` (defaults to now), or None if no visits yet."""
    at = at or datetime.now(timezone.utc)
    start, end = _utc_day_bounds(at)
    row = (
        db.query(VenueVisit)
        .filter(
            and_(
                VenueVisit.venue_id == venue_id,
                VenueVisit.timestamp >= start,
                VenueVisit.timestamp <= end,
                VenueVisit.device_id.is_not(None),
            )
        )
        .order_by(VenueVisit.timestamp.asc())
        .first()
    )
    return row.device_id if row else None


def _already_rewarded(db: Session, venue_id: str, user_id: str, at: datetime) -> bool:
    """Idempotency check via a marker row in UserWallet.user_id namespace.
    We persist an audit row as user_id=`reward:{venue_id}:{YYYY-MM-DD}` with credits=0
    to act as a lightweight dedup ledger; the reward is still added to the real
    wallet row for `user_id`."""
    start, _ = _utc_day_bounds(at)
    marker_id = f"reward:fvv:{venue_id}:{start.strftime('%Y-%m-%d')}"
    existing = db.get(UserWallet, marker_id)
    return existing is not None


def _mark_rewarded(db: Session, venue_id: str, user_id: str, at: datetime) -> None:
    start, _ = _utc_day_bounds(at)
    marker_id = f"reward:fvv:{venue_id}:{start.strftime('%Y-%m-%d')}"
    if db.get(UserWallet, marker_id) is None:
        db.add(UserWallet(user_id=marker_id, credits=0))
        db.commit()


def award_first_verified_visit(
    db: Session, *, venue_id: str, user_id: str, at: Optional[datetime] = None,
) -> dict:
    """Core rule:
      - Venue must currently be verified.
      - Today's first visitor (by UTC day) receives +15 credits.
      - Idempotent: a per-venue-per-day marker prevents double-crediting.

    Returns a dict with the outcome for API surfacing / toast rendering.
    """
    at = at or datetime.now(timezone.utc)
    venue = db.get(Venue, venue_id)
    if not venue:
        return {"awarded": False, "reason": "venue_not_found"}

    if venue_id not in verified_venue_ids(db):
        return {"awarded": False, "reason": "venue_not_verified"}

    first_device = get_first_visit_for_venue_today(db, venue_id, at)
    if not first_device:
        return {"awarded": False, "reason": "no_visits_today"}
    if first_device != user_id:
        return {
            "awarded": False,
            "reason": "not_first_visitor",
            "first_visitor_device_id": first_device,
        }
    if _already_rewarded(db, venue_id, user_id, at):
        return {"awarded": False, "reason": "already_rewarded_today"}

    wallet = add_credits(db, user_id, FIRST_VISIT_BONUS)
    _mark_rewarded(db, venue_id, user_id, at)

    # Fan out as an owner webhook event (OWNER:FIRST_VERIFIED_VISIT).
    try:
        from app.services import webhooks as wh
        wh.dispatch_owner(
            "FIRST_VERIFIED_VISIT",
            venue_id=venue_id,
            title=f"First verified visit · {venue.name}",
            body=f"Device {user_id[:10]}… earned {FIRST_VISIT_BONUS} vibe credits.",
            meta={"venue_id": venue_id, "device_id": user_id, "bonus": FIRST_VISIT_BONUS},
        )
    except Exception as exc:  # pragma: no cover
        logger.debug("owner webhook fan-out failed: %s", exc)

    return {
        "awarded": True,
        "bonus_credits": FIRST_VISIT_BONUS,
        "balance": int(wallet.credits or 0),
        "venue_id": venue_id,
        "venue_name": venue.name,
        "user_id": user_id,
    }


def check_in_and_reward(
    db: Session, *, venue_id: str, user_id: str,
) -> dict:
    """Record a VenueVisit for this (device, venue) at "now" and evaluate the
    first-verified-visit rule. Mobile uses this endpoint as an explicit
    check-in action; the passive detector pipeline also uses it by calling the
    award function after inserting visits."""
    now = datetime.now(timezone.utc)
    db.add(VenueVisit(venue_id=venue_id, device_id=user_id, timestamp=now))
    db.commit()
    return award_first_verified_visit(db, venue_id=venue_id, user_id=user_id, at=now)


def list_first_visit_rewards(
    db: Session, user_id: Optional[str] = None, limit: int = 50,
) -> list[dict]:
    """Return the per-day reward markers (optionally filtered by user) so the
    admin 'wallet history with FIRST_VERIFIED_VISIT filter' view has data."""
    from sqlalchemy import func
    q = (
        db.query(UserWallet)
        .filter(UserWallet.user_id.like("reward:fvv:%"))
        .order_by(UserWallet.updated_at.desc())
        .limit(limit)
    )
    rows = q.all()
    items = []
    for r in rows:
        # id format: reward:fvv:<venue_id>:<YYYY-MM-DD>
        parts = r.user_id.split(":")
        if len(parts) >= 4:
            items.append({
                "kind": "FIRST_VERIFIED_VISIT",
                "venue_id": parts[2],
                "date": parts[3],
                "recorded_at": r.updated_at.isoformat() if r.updated_at else None,
            })
    return items
