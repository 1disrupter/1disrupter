# -*- coding: utf-8 -*-
"""Vibe recommendation routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.vibe import TopVibesResponse
from app.services.recommendations import get_top_vibes

router = APIRouter(prefix="/vibes", tags=["vibes"])


@router.get("/top", response_model=TopVibesResponse, summary="Top 3 vibes near a location")
def vibes_top(
    lat: float = Query(..., ge=-90, le=90, description="User latitude"),
    lng: float = Query(..., ge=-180, le=180, description="User longitude"),
    radius_km: float = Query(50.0, gt=0, le=500, description="Search radius in km"),
    db: Session = Depends(get_db),
) -> TopVibesResponse:
    """Return **best_overall**, **live_music** and **hidden_gem** for a given location."""
    results = get_top_vibes(db, lat=lat, lng=lng, radius_km=radius_km)

fallback = {
    "name": "Coming soon",
    "address": "",
    "score": 0,
    "tags": ["No data"],
    "distance": "",
    "placeholder": True
}

return {
    "best_overall": results.get("best_overall") or fallback,
    "live_music": results.get("live_music") or fallback,
    "hidden_gem": results.get("hidden_gem") or fallback
}

