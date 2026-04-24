# -*- coding: utf-8 -*-
"""Social activity signal.

If INSTAGRAM_ACCESS_TOKEN or TIKTOK_ACCESS_TOKEN is configured the real
provider is queried first; otherwise the deterministic stub is used so
behaviour is unchanged for installs without keys.
"""
from app.services.signals._common import baseline_for, clamp, live_jitter
from app.services.signals import providers


async def get_social_activity_score(venue) -> float:
    """Return a 0–10 score representing recent social-media activity."""
    real = await providers.first_available(providers.SOCIAL_PROVIDERS, venue)
    if real is not None:
        return clamp(real)
    # Fallback — stub baseline + jitter.
    base = baseline_for(venue, "social", low=2.5, high=9.2)
    return clamp(base + live_jitter(0.8))
