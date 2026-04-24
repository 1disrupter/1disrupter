# -*- coding: utf-8 -*-
"""Enriched venue list & scoring — additive endpoints that include travel time."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Venue, Vibe, VenueSignals
from app.services.maps import get_travel_time
from app.services.venues.ownership import verified_venue_ids

router = APIRouter(tags=["venues-ext"])


def _serialize(v: Venue, vibe: Vibe | None, sig: VenueSignals | None,
               user_lat: Optional[float], user_lng: Optional[float],
               is_verified: bool = False) -> dict:
    out = {
        "id": v.id,
        "name": v.name,
        "category": v.category.value if hasattr(v.category, "value") else v.category,
        "lat": v.latitude,
        "lng": v.longitude,
        "is_verified": bool(is_verified),
        "vibe_score": float(vibe.vibe_score or 0.0) if vibe else 0.0,
        "crowd_level": (
            vibe.crowd_level.value if vibe and hasattr(vibe.crowd_level, "value") else (vibe.crowd_level if vibe else None)
        ),
        "external_signals": sig.as_dict() if sig else None,
    }
    if user_lat is not None and user_lng is not None:
        tt = get_travel_time(user_lat, user_lng, v.latitude, v.longitude)
        out.update({
            "distance_km": tt["distance_km"],
            "walking_time_minutes": tt["walking_time_minutes"],
            "driving_time_minutes": tt["driving_time_minutes"],
            "travel_provider": tt["provider"],
        })
    return out


@router.get("/venues/list", summary="Venues with optional travel-time enrichment")
def venues_list(
    user_lat: Optional[float] = Query(None, ge=-90, le=90),
    user_lng: Optional[float] = Query(None, ge=-180, le=180),
    verified_only: bool = Query(False, description="Only return verified venues"),
    db: Session = Depends(get_db),
):
    rows = db.query(Venue, Vibe).join(Vibe, Venue.id == Vibe.venue_id).all()
    signals = {s.venue_id: s for s in db.query(VenueSignals).all()}
    verified = verified_venue_ids(db)
    items = []
    for v, vibe in rows:
        if verified_only and v.id not in verified:
            continue
        items.append(_serialize(v, vibe, signals.get(v.id), user_lat, user_lng, v.id in verified))
    return {"count": len(items), "items": items}


@router.get("/intel/score/{venue_id}", summary="Rich score + travel-time for a single venue")
def intel_score(
    venue_id: str,
    user_lat: Optional[float] = Query(None, ge=-90, le=90),
    user_lng: Optional[float] = Query(None, ge=-180, le=180),
    db: Session = Depends(get_db),
):
    v = db.get(Venue, venue_id)
    if not v:
        raise HTTPException(status_code=404, detail="venue not found")
    vibe = db.get(Vibe, venue_id)
    sig = db.query(VenueSignals).filter(VenueSignals.venue_id == venue_id).one_or_none()
    is_verified = venue_id in verified_venue_ids(db)
    return _serialize(v, vibe, sig, user_lat, user_lng, is_verified)
