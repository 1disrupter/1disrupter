# -*- coding: utf-8 -*-
"""Vibe-score trajectory history.

Every 5 minutes the scheduler appends a snapshot of every venue's current
vibe score into `venue_vibe_history`. Used by the forecast module and the
admin UI to draw real trajectory graphs.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy.orm import Session

from app.models import Vibe, VenueVibeHistory


def append_current_scores(db: Session) -> int:
    """Snapshot every Vibe row into the history table. Returns rows written."""
    now = datetime.now(timezone.utc)
    rows = db.query(Vibe).all()
    written = 0
    for v in rows:
        db.add(VenueVibeHistory(
            venue_id=v.venue_id,
            vibe_score=float(v.vibe_score or 0.0),
            timestamp=now,
        ))
        written += 1
    if written:
        db.commit()
    return written


def get_trajectory(
    db: Session, venue_id: str, hours: int = 6, limit: int = 200,
) -> List[VenueVibeHistory]:
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    return (
        db.query(VenueVibeHistory)
        .filter(
            VenueVibeHistory.venue_id == venue_id,
            VenueVibeHistory.timestamp >= since,
        )
        .order_by(VenueVibeHistory.timestamp.asc())
        .limit(limit)
        .all()
    )
