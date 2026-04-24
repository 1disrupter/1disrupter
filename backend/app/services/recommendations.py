# -*- coding: utf-8 -*-
"""Recommendation engine: build the best_overall / live_music / hidden_gem response."""
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Venue, Vibe, VenueCategory
from app.schemas.vibe import VenueOut, VibeOut, SignalsOut, VibeResult, TopVibesResponse
from app.services.geo import haversine_km
from app.services.venues.ownership import verified_venue_ids


def _to_result(venue: Venue, vibe: Vibe, user_lat: float, user_lng: float,
               verified: set[str]) -> VibeResult:
    vo = VenueOut.model_validate(venue)
    vo.is_verified = venue.id in verified
    return VibeResult(
        venue=vo,
        vibe=VibeOut(
            venue_id=vibe.venue_id,
            vibe_score=vibe.vibe_score,
            crowd_level=vibe.crowd_level,
            last_updated=vibe.last_updated,
            signals=SignalsOut(**vibe.signals_dict()),
        ),
        distance_km=haversine_km(user_lat, user_lng, venue.latitude, venue.longitude),
    )


def get_top_vibes(
    db: Session, lat: float, lng: float, radius_km: float = 50.0
) -> TopVibesResponse:
    """Return best_overall, live_music and hidden_gem within radius_km of (lat, lng)."""
    rows = (
        db.query(Venue, Vibe)
        .join(Vibe, Venue.id == Vibe.venue_id)
        .all()
    )

    # Filter by haversine radius
    in_range: list[tuple[Venue, Vibe, float]] = []
    for venue, vibe in rows:
        d = haversine_km(lat, lng, venue.latitude, venue.longitude)
        if d <= radius_km:
            in_range.append((venue, vibe, d))

    if not in_range:
        return TopVibesResponse(best_overall=None, live_music=None, hidden_gem=None)

    verified = verified_venue_ids(db)

    best = max(in_range, key=lambda t: t[1].vibe_score)
    gem = min(in_range, key=lambda t: t[1].vibe_score)
    lm_candidates = [t for t in in_range if t[0].category == VenueCategory.live_music]
    lm = max(lm_candidates, key=lambda t: t[1].vibe_score) if lm_candidates else best

    def _build(triplet) -> Optional[VibeResult]:
        v, vb, _ = triplet
        return _to_result(v, vb, lat, lng, verified)

    return TopVibesResponse(
        best_overall=_build(best),
        live_music=_build(lm),
        hidden_gem=_build(gem),
    )
