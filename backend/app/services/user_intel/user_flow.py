# -*- coding: utf-8 -*-
"""User-flow detection.

For each venue, compare the number of pings currently "close" to the venue
vs. those close 10-15 minutes ago:
  • growing population       → rising
  • stable high population   → peaking
  • shrinking population     → falling
  • low stable population    → steady
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy.orm import Session

from app.models import UserLocationPing, Venue
from app.services.geo import haversine_km

PROXIMITY_KM = 0.08        # 80 m — close enough to count as "at the venue"
CURRENT_WINDOW_MIN = 5
PAST_WINDOW_MIN_FROM = 15
PAST_WINDOW_MIN_TO = 10    # 10–15 min ago


def _count_nearby(pings: List[UserLocationPing], venue: Venue) -> int:
    n = 0
    for p in pings:
        if haversine_km(p.lat, p.lng, venue.latitude, venue.longitude) <= PROXIMITY_KM:
            n += 1
    return n


def compute_flow(db: Session) -> list[dict]:
    now = datetime.now(timezone.utc)
    cur_from = now - timedelta(minutes=CURRENT_WINDOW_MIN)
    past_from = now - timedelta(minutes=PAST_WINDOW_MIN_FROM)
    past_to = now - timedelta(minutes=PAST_WINDOW_MIN_TO)

    cur = (
        db.query(UserLocationPing)
        .filter(UserLocationPing.timestamp >= cur_from)
        .all()
    )
    past = (
        db.query(UserLocationPing)
        .filter(UserLocationPing.timestamp >= past_from, UserLocationPing.timestamp < past_to)
        .all()
    )
    venues = db.query(Venue).all()

    out = []
    for v in venues:
        c = _count_nearby(cur, v)
        p = _count_nearby(past, v)
        if c >= 3 and abs(c - p) <= max(1, int(0.2 * max(c, p))):
            flow = "peaking"
        elif c > p:
            flow = "rising"
        elif c < p:
            flow = "falling"
        else:
            flow = "steady"
        out.append({
            "venue_id": v.id,
            "name": v.name,
            "flow": flow,
            "pings_now": c,
            "pings_past": p,
        })
    return out
