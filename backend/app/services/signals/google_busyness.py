# -*- coding: utf-8 -*-
"""Google busyness signal.

If GOOGLE_PLACES_API_KEY is configured the real Google Places adapter is
queried first; otherwise the deterministic stub is used.
"""
from app.services.signals._common import baseline_for, clamp, live_jitter
from app.services.signals import providers


async def get_google_busyness_score(venue) -> float:
    """Return a 0–10 score representing live Google busyness."""
    real = await providers.first_available(providers.BUSYNESS_PROVIDERS, venue)
    if real is not None:
        return clamp(real)
    base = baseline_for(venue, "google", low=3.0, high=9.0)
    return clamp(base + live_jitter(0.4))
