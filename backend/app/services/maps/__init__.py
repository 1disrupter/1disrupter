# -*- coding: utf-8 -*-
"""Google Distance Matrix wrapper with in-memory 5-min cache.

Falls back to a haversine-derived stub when GOOGLE_MAPS_API_KEY is unset.
Never raises into caller routes.
"""
from __future__ import annotations

import logging
import time
from typing import Optional

import requests

from app.core.config import get_settings
from app.services.geo import haversine_km

logger = logging.getLogger("vibe2nite.maps")

CACHE_TTL_S = 300  # 5 minutes
_cache: dict[tuple, tuple[float, dict]] = {}

WALK_SPEED_KMH = 4.8      # ~3 mph
DRIVE_SPEED_KMH = 28.0    # urban-ish


def _cache_key(user_lat: float, user_lng: float, venue_lat: float, venue_lng: float) -> tuple:
    # Round to ~100m to keep the cache warm but accurate enough.
    def r(x: float) -> float:
        return round(x, 3)
    return (r(user_lat), r(user_lng), r(venue_lat), r(venue_lng))


def _stub_payload(user_lat: float, user_lng: float, venue_lat: float, venue_lng: float) -> dict:
    km = haversine_km(user_lat, user_lng, venue_lat, venue_lng)
    walking = (km / WALK_SPEED_KMH) * 60.0
    driving = (km / DRIVE_SPEED_KMH) * 60.0
    return {
        "provider": "stub",
        "distance_km": round(km, 3),
        "walking_time_minutes": round(walking, 1),
        "driving_time_minutes": round(driving, 1),
    }


def _google_payload(
    user_lat: float, user_lng: float, venue_lat: float, venue_lng: float, api_key: str,
) -> Optional[dict]:
    base = "https://maps.googleapis.com/maps/api/distancematrix/json"
    try:
        r = requests.get(
            base,
            params={
                "origins": f"{user_lat},{user_lng}",
                "destinations": f"{venue_lat},{venue_lng}",
                "mode": "walking",  # walking first — we'll add driving with a 2nd call
                "key": api_key,
            },
            timeout=4,
        )
        r.raise_for_status()
        w = r.json()

        r2 = requests.get(
            base,
            params={
                "origins": f"{user_lat},{user_lng}",
                "destinations": f"{venue_lat},{venue_lng}",
                "mode": "driving",
                "key": api_key,
            },
            timeout=4,
        )
        r2.raise_for_status()
        d = r2.json()

        w_elem = w["rows"][0]["elements"][0]
        d_elem = d["rows"][0]["elements"][0]
        if w_elem.get("status") != "OK" or d_elem.get("status") != "OK":
            return None
        return {
            "provider": "google",
            "distance_km": round(float(w_elem["distance"]["value"]) / 1000.0, 3),
            "walking_time_minutes": round(float(w_elem["duration"]["value"]) / 60.0, 1),
            "driving_time_minutes": round(float(d_elem["duration"]["value"]) / 60.0, 1),
        }
    except Exception as exc:  # pragma: no cover
        logger.warning("distance-matrix google fetch failed: %s", exc)
        return None


def get_travel_time(
    user_lat: float, user_lng: float, venue_lat: float, venue_lng: float,
) -> dict:
    """Return {provider, distance_km, walking_time_minutes, driving_time_minutes}.
    Cached for 5 minutes."""
    key = _cache_key(user_lat, user_lng, venue_lat, venue_lng)
    hit = _cache.get(key)
    now = time.time()
    if hit and now - hit[0] < CACHE_TTL_S:
        return {**hit[1], "cached": True}

    settings = get_settings()
    payload: Optional[dict] = None
    if settings.GOOGLE_MAPS_API_KEY:
        payload = _google_payload(user_lat, user_lng, venue_lat, venue_lng, settings.GOOGLE_MAPS_API_KEY)
    if payload is None:
        payload = _stub_payload(user_lat, user_lng, venue_lat, venue_lng)

    _cache[key] = (now, payload)
    return {**payload, "cached": False}


def clear_cache() -> int:
    """Test/debug helper."""
    n = len(_cache)
    _cache.clear()
    return n
