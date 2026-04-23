# -*- coding: utf-8 -*-
"""Extra /vibes endpoints built on top of the Signal Engine.

Existing `/api/vibes/top` is unchanged (see app/routers/vibes.py). This file
adds directions, heatmap, live-music, tourist-flags, forecast and an upgraded
top3 endpoint — all additive.
"""
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Venue
from app.services.directions import get_directions
from app.services.heatmap import build_heatmap
from app.services.live_music import detect_live_music
from app.services.tourist_trap import classify_all
from app.services.vibe_forecast import forecast_all, forecast_one
from app.services.top3 import get_top3

router = APIRouter(prefix="/vibes", tags=["vibes-extras"])


# ---------------------------------------------------------------------------
# 1. Directions
# ---------------------------------------------------------------------------
@router.get("/directions", summary="Walking ETA, distance & Maps deeplink")
async def directions(
    venue_id: str = Query(..., min_length=1),
    user_lat: float = Query(..., ge=-90, le=90),
    user_lng: float = Query(..., ge=-180, le=180),
    db: Session = Depends(get_db),
):
    venue = db.get(Venue, venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="venue_id not found")
    result = await get_directions(venue, user_lat, user_lng)
    return result.as_dict()


# ---------------------------------------------------------------------------
# 2. Heat map
# ---------------------------------------------------------------------------
@router.get("/heatmap", summary="Per-venue heat points for map overlays")
def heatmap(
    categories: Optional[List[str]] = Query(None, description="Filter by one or more categories"),
    db: Session = Depends(get_db),
):
    points = build_heatmap(db, categories=categories)
    return {"count": len(points), "points": points}


# ---------------------------------------------------------------------------
# 3. Live-music detection
# ---------------------------------------------------------------------------
@router.get("/live-music", summary="Venues likely to have live music now")
def live_music(
    all_flag: bool = Query(False, alias="include_all", description="Include non-flagged venues"),
    db: Session = Depends(get_db),
):
    items = detect_live_music(db, only_flagged=not all_flag)
    return {"count": len(items), "items": items}


# ---------------------------------------------------------------------------
# 4. Tourist-trap / local-gem classifier
# ---------------------------------------------------------------------------
@router.get("/tourist-flags", summary="Tourist-trap / local-gem classification")
def tourist_flags(db: Session = Depends(get_db)):
    items = classify_all(db)
    buckets = {"tourist_trap": 0, "local_gem": 0, "neutral": 0}
    for it in items:
        buckets[it["label"]] = buckets.get(it["label"], 0) + 1
    return {"count": len(items), "buckets": buckets, "items": items}


# ---------------------------------------------------------------------------
# 5. Vibe forecast
# ---------------------------------------------------------------------------
@router.get("/forecast", summary="Short-term trend: rising / peaking / falling / steady")
def forecast(
    venue_id: Optional[str] = Query(None, description="If omitted, returns all venues"),
    db: Session = Depends(get_db),
):
    if venue_id:
        item = forecast_one(db, venue_id)
        if not item:
            raise HTTPException(status_code=404, detail="venue_id not found")
        return item
    items = forecast_all(db)
    return {"count": len(items), "items": items}


# ---------------------------------------------------------------------------
# 6. Enhanced Top-3
# ---------------------------------------------------------------------------
VibeFilter = Literal["bar", "club", "live_music"]


@router.get("/top3", summary="Enhanced Top-3 recommendation (filter + distance + tourist-avoid)")
def top3(
    user_lat: Optional[float] = Query(None, ge=-90, le=90),
    user_lng: Optional[float] = Query(None, ge=-180, le=180),
    vibe: Optional[VibeFilter] = Query(None, description="Filter by category"),
    avoid_tourist_traps: bool = Query(False),
    radius_km: Optional[float] = Query(None, gt=0, le=500),
    db: Session = Depends(get_db),
):
    items = get_top3(
        db,
        user_lat=user_lat, user_lng=user_lng,
        vibe=vibe, avoid_tourist_traps=avoid_tourist_traps,
        radius_km=radius_km,
    )
    return {"count": len(items), "items": items}
