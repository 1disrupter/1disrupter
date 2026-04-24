# -*- coding: utf-8 -*-
"""Event signal.

If a real event provider (Ticketmaster / Eventbrite) is configured its score
is used; otherwise the deterministic stub (category-aware baseline) is used.
"""
from app.services.signals._common import baseline_for, clamp
from app.services.signals import providers

# Boost when the venue category implies live entertainment (stub-only).
CATEGORY_BOOST = {
    "live_music": 3.5,
    "club": 1.5,
    "bar": 0.0,
}


async def get_event_signal_score(venue) -> float:
    """Return a 0–10 score representing live-music / event likelihood tonight."""
    real = await providers.first_available(providers.EVENT_PROVIDERS, venue)
    if real is not None:
        return clamp(real)
    category = getattr(getattr(venue, "category", None), "value", None) or str(getattr(venue, "category", "bar"))
    base = baseline_for(venue, "events", low=1.0, high=6.0)
    return clamp(base + CATEGORY_BOOST.get(category, 0.0))
