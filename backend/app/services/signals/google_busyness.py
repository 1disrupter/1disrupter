# -*- coding: utf-8 -*-
"""Google busyness signal (stubbed).

Future integration: Google Places API + Popular Times / live busyness.
Reference: https://developers.google.com/maps/documentation/places
"""
from app.services.signals._common import baseline_for, clamp, live_jitter


async def get_google_busyness_score(venue) -> float:
    """Return a 0–10 score representing live Google busyness."""
    # TODO: integrate Google Places / Popular Times
    base = baseline_for(venue, "google", low=3.0, high=9.0)
    return clamp(base + live_jitter(0.4))
