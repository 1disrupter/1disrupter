# -*- coding: utf-8 -*-
"""User-feedback-derived signal.

Reads the last `WINDOW_MIN` minutes of FeedbackLog rows for this venue and
converts them to a 0..10 score. Fresh votes dominate.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import FeedbackLog
from app.models.feedback import VoteType
from app.services.signals._common import clamp

WINDOW_MIN = 120  # consider votes from the last 2 hours

VOTE_WEIGHT = {
    VoteType.busy: +2.0,
    VoteType.good: +1.0,
    VoteType.dead: -2.0,
}


async def get_user_feedback_score(venue, db: Optional[Session] = None) -> float:
    """Turn recent feedback into a 0..10 score (neutral baseline = 5)."""
    owns_session = db is None
    session: Session = db or SessionLocal()
    try:
        since = datetime.now(timezone.utc) - timedelta(minutes=WINDOW_MIN)
        rows = (
            session.query(FeedbackLog)
            .filter(
                FeedbackLog.venue_id == venue.id,
                FeedbackLog.created_at >= since,
            )
            .all()
        )
        if not rows:
            return 5.0  # neutral baseline when no recent feedback
        delta = sum(VOTE_WEIGHT.get(r.vote, 0.0) for r in rows)
        # Cap contribution so a burst doesn't saturate.
        delta = max(-5.0, min(5.0, delta))
        return clamp(5.0 + delta)
    finally:
        if owns_session:
            session.close()
