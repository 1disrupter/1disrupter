# -*- coding: utf-8 -*-
"""Venue-visit detection.

Rule (spec):
  ping within 40 m of a venue AND device stayed > 5 min → record a visit.

Implementation: scan recent pings, bucket by (device_id, venue) pairs where
the ping is within the radius; if the bucket spans at least MIN_DWELL_MIN,
record a single VenueVisit row (idempotent via a lookup on the latest).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models import UserLocationPing, Venue, VenueVisit
from app.services.geo import haversine_km

PROXIMITY_M = 40
MIN_DWELL_MIN = 5
LOOKBACK_MIN = 60
# Avoid writing duplicate visits for the same (device, venue) within this window.
DEDUPE_WINDOW_MIN = 30


def _km(m: float) -> float:
    return m / 1000.0


def detect_visits(db: Session) -> int:
    """Run the visit detector once. Returns number of new visits created."""
    now = datetime.now(timezone.utc)
    since = now - timedelta(minutes=LOOKBACK_MIN)

    venues = db.query(Venue).all()
    pings = (
        db.query(UserLocationPing)
        .filter(UserLocationPing.timestamp >= since)
        .filter(UserLocationPing.device_id.is_not(None))
        .order_by(UserLocationPing.timestamp.asc())
        .all()
    )
    if not pings or not venues:
        return 0

    created = 0
    radius_km = _km(PROXIMITY_M)
    buckets: dict[tuple[str, str], list[UserLocationPing]] = {}

    for p in pings:
        for v in venues:
            if haversine_km(p.lat, p.lng, v.latitude, v.longitude) <= radius_km:
                buckets.setdefault((p.device_id or "", v.id), []).append(p)

    for (device_id, venue_id), items in buckets.items():
        if not items:
            continue
        span_min = (items[-1].timestamp - items[0].timestamp).total_seconds() / 60.0
        if span_min < MIN_DWELL_MIN:
            continue

        # Dedup: skip if we already stored a visit for this (device, venue) recently.
        cutoff = now - timedelta(minutes=DEDUPE_WINDOW_MIN)
        recent = (
            db.query(VenueVisit)
            .filter(
                and_(
                    VenueVisit.venue_id == venue_id,
                    VenueVisit.device_id == (device_id or None),
                    VenueVisit.timestamp >= cutoff,
                )
            )
            .first()
        )
        if recent:
            continue

        db.add(VenueVisit(
            venue_id=venue_id,
            device_id=device_id or None,
            timestamp=items[-1].timestamp,
        ))
        created += 1

    if created:
        db.commit()
    return created


def list_visits(db: Session, venue_id: str, limit: int = 50) -> List[VenueVisit]:
    return (
        db.query(VenueVisit)
        .filter(VenueVisit.venue_id == venue_id)
        .order_by(VenueVisit.timestamp.desc())
        .limit(limit)
        .all()
    )
