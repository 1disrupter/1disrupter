# -*- coding: utf-8 -*-
"""Signal Engine — composes the five per-venue signal sources."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.services.signals.google_busyness import get_google_busyness_score
from app.services.signals.social_activity import get_social_activity_score
from app.services.signals.event_signals import get_event_signal_score
from app.services.signals.time_patterns import get_time_pattern_score
from app.services.signals.user_feedback_signal import get_user_feedback_score


async def compute_signals_for_venue(venue, db: Optional[Session] = None) -> dict:
    """Return the five signal scores for a venue."""
    return {
        "google": await get_google_busyness_score(venue),
        "social": await get_social_activity_score(venue),
        "events": await get_event_signal_score(venue),
        "time": await get_time_pattern_score(venue),
        "votes": await get_user_feedback_score(venue, db=db),
    }
