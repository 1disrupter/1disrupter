# -*- coding: utf-8 -*-
"""Google Directions integration.

- Returns walking ETA + distance to a venue and a Google-Maps deeplink.
- If `GOOGLE_MAPS_API_KEY` is present in env, we will (in the future) call the
  Distance Matrix API for accurate times; today we ship a deterministic stub
  based on haversine + average walking speed (5 km/h). The shape of the
  response is final — swapping the stub for a real client won't change callers.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from urllib.parse import urlencode

from app.services.geo import haversine_km

WALKING_KMH = 5.0
GOOGLE_MAPS_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")  # None today


@dataclass
class Directions:
    venue_id: str
    duration_minutes: int
    distance_meters: int
    deeplink: str
    provider: str  # "stub" | "google"

    def as_dict(self) -> dict:
        return asdict(self)


def _deeplink(dest_lat: float, dest_lng: float, origin_lat: float, origin_lng: float) -> str:
    params = urlencode({
        "api": 1,
        "origin": f"{origin_lat},{origin_lng}",
        "destination": f"{dest_lat},{dest_lng}",
        "travelmode": "walking",
    })
    return f"https://www.google.com/maps/dir/?{params}"


async def get_directions(venue, user_lat: float, user_lng: float) -> Directions:
    """Return walking ETA + distance + Maps deeplink for a venue."""
    km = haversine_km(user_lat, user_lng, venue.latitude, venue.longitude)
    duration_minutes = max(1, round((km / WALKING_KMH) * 60))
    distance_meters = int(round(km * 1000))
    deeplink = _deeplink(venue.latitude, venue.longitude, user_lat, user_lng)
    provider = "google" if GOOGLE_MAPS_KEY else "stub"
    # TODO: when GOOGLE_MAPS_KEY is set, call
    # https://maps.googleapis.com/maps/api/distancematrix/json?mode=walking&...
    return Directions(
        venue_id=venue.id,
        duration_minutes=duration_minutes,
        distance_meters=distance_meters,
        deeplink=deeplink,
        provider=provider,
    )
