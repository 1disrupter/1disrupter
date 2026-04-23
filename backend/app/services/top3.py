# -*- coding: utf-8 -*-
"""Top-3 recommendation upgrade.

New ranker that layers on top of the existing `recommendations.get_top_vibes`
- does NOT replace it. Adds:

  • Optional vibe (category) filter: bar / club / live_music
  • Optional distance penalty when user coords are provided
  • Optional tourist-trap avoidance

Exposed via `/api/vibes/top3` (separate from the existing `/api/vibes/top`).
"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Venue, Vibe, VenueSignals
from app.models.venue import VenueCategory
from app.services.geo import haversine_km
from app.services.tourist_trap import classify, LABEL_TOURIST

# Distance penalty: how many score-points we subtract per km of walking.
# 0.05 means a venue 10 km away loses 0.5 off its score — mild but present.
DISTANCE_PENALTY_PER_KM = 0.05

# Soft tourist-trap penalty. Applied *only* when avoid_tourist_traps=False
# (when True the venue is excluded outright). A labelled trap still ranks,
# just 2 points lower so a local gem nearby beats it.
TOURIST_PENALTY = 2.0


def _category_match(venue: Venue, vibe_filter: Optional[str]) -> bool:
    if not vibe_filter:
        return True
    try:
        target = VenueCategory(vibe_filter)
    except ValueError:
        return False
    return venue.category == target


def get_top3(
    db: Session,
    *,
    user_lat: Optional[float] = None,
    user_lng: Optional[float] = None,
    vibe: Optional[str] = None,
    avoid_tourist_traps: bool = False,
    radius_km: Optional[float] = None,
) -> List[dict]:
    rows = (
        db.query(Venue, Vibe, VenueSignals)
        .join(Vibe, Vibe.venue_id == Venue.id)
        .outerjoin(VenueSignals, VenueSignals.venue_id == Venue.id)
        .all()
    )

    ranked: list[tuple[float, dict]] = []
    for venue, v, sig in rows:
        if not _category_match(venue, vibe):
            continue

        distance_km: Optional[float] = None
        if user_lat is not None and user_lng is not None:
            distance_km = haversine_km(user_lat, user_lng, venue.latitude, venue.longitude)
            if radius_km is not None and distance_km > radius_km:
                continue

        label, _reason = classify(sig)
        if avoid_tourist_traps and label == LABEL_TOURIST:
            continue

        base = float(v.vibe_score or 0.0)
        adjusted = base
        if distance_km is not None:
            adjusted -= DISTANCE_PENALTY_PER_KM * distance_km
        if avoid_tourist_traps is False and label == LABEL_TOURIST:
            adjusted -= TOURIST_PENALTY
        adjusted = max(0.0, min(10.0, adjusted))

        ranked.append((adjusted, {
            "id": venue.id,
            "name": venue.name,
            "category": venue.category.value,
            "vibe_score": round(base, 2),
            "adjusted_score": round(adjusted, 2),
            "lat": venue.latitude,
            "lng": venue.longitude,
            "distance_km": round(distance_km, 3) if distance_km is not None else None,
            "tourist_label": label,
        }))

    ranked.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in ranked[:3]]
