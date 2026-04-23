# -*- coding: utf-8 -*-
"""Event signal (stubbed).

Future integration: Songkick / Bandsintown / Eventbrite / Resident Advisor
for scheduled DJ / live-band events at the venue tonight.
"""
from app.services.signals._common import baseline_for, clamp

# Boost when the venue category implies live entertainment.
CATEGORY_BOOST = {
    "live_music": 3.5,
    "club": 1.5,
    "bar": 0.0,
}


async def get_event_signal_score(venue) -> float:
    """Return a 0–10 score representing live-music / event likelihood tonight."""
    # TODO: detect live music / DJ events from a real provider
    category = getattr(getattr(venue, "category", None), "value", None) or str(getattr(venue, "category", "bar"))
    base = baseline_for(venue, "events", low=1.0, high=6.0)
    return clamp(base + CATEGORY_BOOST.get(category, 0.0))
