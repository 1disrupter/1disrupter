# -*- coding: utf-8 -*-
"""Social activity signal (stubbed).

Future integration: Instagram / TikTok / Twitter hashtag or geo-tag velocity
for the venue's handle(s).
"""
from app.services.signals._common import baseline_for, clamp, live_jitter


async def get_social_activity_score(venue) -> float:
    """Return a 0–10 score representing recent social-media activity."""
    # TODO: Instagram / TikTok / X velocity API
    base = baseline_for(venue, "social", low=2.5, high=9.2)
    return clamp(base + live_jitter(0.8))
