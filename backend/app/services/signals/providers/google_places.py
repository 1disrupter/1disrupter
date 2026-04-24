# -*- coding: utf-8 -*-
"""Google Places adapter — real busyness score when key present."""
from __future__ import annotations

import logging
import os
from typing import Optional

import requests

NAME = "google_places"
ENV_VAR = "GOOGLE_PLACES_API_KEY"

logger = logging.getLogger("vibe2nite.providers.google_places")


def is_configured() -> bool:
    return bool(os.environ.get(ENV_VAR, "").strip())


async def fetch(venue) -> Optional[float]:
    """Return a 0..10 busyness-style score.

    Google Places API v2 (New) does not expose Popular Times as a public field,
    so we proxy "busyness" via `currentOpeningHours.openNow` + `userRatingCount`
    normalization. This is intentionally approximate — owners who want real
    busyness need the Places (Live) API partner program.
    """
    key = os.environ.get(ENV_VAR, "").strip()
    if not key:
        return None
    try:
        # Find-place-from-text (no places-id on file yet). Name + coords give a
        # decent match for most venues we ingest via OSM.
        q = requests.get(
            "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
            params={
                "input": venue.name,
                "inputtype": "textquery",
                "fields": "rating,user_ratings_total,opening_hours",
                "locationbias": f"circle:200@{venue.latitude},{venue.longitude}",
                "key": key,
            },
            timeout=4,
        )
        q.raise_for_status()
        candidates = q.json().get("candidates") or []
        if not candidates:
            return None
        top = candidates[0]
        open_now = bool((top.get("opening_hours") or {}).get("open_now", False))
        rating = float(top.get("rating") or 0.0)
        votes  = int(top.get("user_ratings_total") or 0)
        # Normalize rating (0..5) → (0..10), push up for "open now", scale by popularity.
        base = rating * 2.0
        if open_now:
            base += 1.2
        # Popularity boost capped at +1.5
        base += min(1.5, (votes / 500.0))
        return max(0.0, min(10.0, base))
    except Exception as exc:  # pragma: no cover
        logger.debug("google_places fetch failed: %s", exc)
        return None
