# -*- coding: utf-8 -*-
"""Heat-Map API layer.

Computes a 0–10 "heat" score per venue from the cached VenueSignals row.
Different from the published `vibe_score`: heat emphasises **density/activity
right now** rather than overall quality, which is what map overlays want.

Formula:
    heat = 0.40 * google_score       (live busyness)
         + 0.30 * social_score       (online buzz)
         + 0.20 * user_votes_score   (recent crowd votes)
         + 0.10 * event_score        (live events on tonight)
Clamped to [0, 10].
"""
from __future__ import annotations

from typing import Iterable, List

from sqlalchemy.orm import Session

from app.models import Venue, VenueSignals

WEIGHTS = {
    "google_score": 0.40,
    "social_score": 0.30,
    "user_votes_score": 0.20,
    "event_score": 0.10,
}


def heat_score(signals: VenueSignals | None) -> float:
    """Return the heat score for a single signals row (0 if missing)."""
    if signals is None:
        return 0.0
    raw = sum(float(getattr(signals, k, 0.0) or 0.0) * w for k, w in WEIGHTS.items())
    return round(min(max(raw, 0.0), 10.0), 2)


def build_heatmap(db: Session, categories: Iterable[str] | None = None) -> List[dict]:
    """Return a list of `{id, name, category, lat, lng, heat}` points."""
    q = db.query(Venue, VenueSignals).outerjoin(
        VenueSignals, Venue.id == VenueSignals.venue_id
    )
    rows = q.all()
    cats = {c for c in (categories or [])}
    out = []
    for venue, signals in rows:
        cat_value = venue.category.value if hasattr(venue.category, "value") else str(venue.category)
        if cats and cat_value not in cats:
            continue
        out.append({
            "id": venue.id,
            "name": venue.name,
            "category": cat_value,
            "lat": venue.latitude,
            "lng": venue.longitude,
            "heat": heat_score(signals),
        })
    # Hottest first — useful for clients that only render the top-N pins.
    out.sort(key=lambda x: x["heat"], reverse=True)
    return out
