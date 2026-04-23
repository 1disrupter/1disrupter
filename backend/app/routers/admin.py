# -*- coding: utf-8 -*-
"""Admin routes — venue listing and manual signal updates (future auth to be added)."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Venue, Vibe, VenueSignals
from app.models.venue import VenueCategory
from app.schemas.vibe import VenueOut, VibeOut, SignalsOut
from app.services.scoring import compute_vibe_score, crowd_level_from_score

router = APIRouter(prefix="/admin", tags=["admin"])


class VenueCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    category: VenueCategory
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class SignalsUpdate(BaseModel):
    manual_score: Optional[float] = Field(None, ge=0, le=10)
    social_activity: Optional[float] = Field(None, ge=0, le=10)
    time_prediction: Optional[float] = Field(None, ge=0, le=10)
    venue_boost: Optional[float] = Field(None, ge=0, le=10)


@router.get("/venues", summary="List all venues with current vibe")
def list_venues(db: Session = Depends(get_db)):
    rows = db.query(Venue, Vibe).join(Vibe, Venue.id == Vibe.venue_id).all()
    # Pre-load signals for the shown venues in one query
    signals_map = {
        s.venue_id: s for s in db.query(VenueSignals).all()
    }
    items = []
    for venue, vibe in rows:
        ext = signals_map.get(venue.id)
        items.append({
            "venue": VenueOut.model_validate(venue).model_dump(),
            "vibe": VibeOut(
                venue_id=vibe.venue_id,
                vibe_score=vibe.vibe_score,
                crowd_level=vibe.crowd_level,
                last_updated=vibe.last_updated,
                signals=SignalsOut(**vibe.signals_dict()),
            ).model_dump(),
            "external_signals": ext.as_dict() if ext else None,
        })
    return {"count": len(items), "items": items}


@router.post("/signals/refresh", summary="Trigger a one-off signal refresh")
async def trigger_refresh():
    """Kick the scheduler's refresh job on-demand (in addition to the 5-min cron)."""
    from app.services.scheduler import refresh_all_signals
    return await refresh_all_signals()


@router.post("/venues", response_model=VenueOut, status_code=201, summary="Create a venue")
def create_venue(payload: VenueCreate, db: Session = Depends(get_db)):
    venue = Venue(
        name=payload.name,
        category=payload.category,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    db.add(venue)
    db.flush()
    db.add(Vibe(venue_id=venue.id))
    db.commit()
    db.refresh(venue)
    return VenueOut.model_validate(venue)


@router.patch("/venues/{venue_id}/signals", response_model=VibeOut, summary="Update manual signals")
def update_signals(venue_id: str, payload: SignalsUpdate, db: Session = Depends(get_db)):
    vibe = db.get(Vibe, venue_id)
    if not vibe:
        raise HTTPException(status_code=404, detail="vibe not found for venue_id")
    for field in ("manual_score", "social_activity", "time_prediction", "venue_boost"):
        val = getattr(payload, field)
        if val is not None:
            setattr(vibe, field, float(val))
    vibe.vibe_score = compute_vibe_score(vibe.signals_dict())
    vibe.crowd_level = crowd_level_from_score(vibe.vibe_score)
    from datetime import datetime, timezone
    vibe.last_updated = datetime.now(timezone.utc)
    db.commit()
    db.refresh(vibe)
    return VibeOut(
        venue_id=vibe.venue_id,
        vibe_score=vibe.vibe_score,
        crowd_level=vibe.crowd_level,
        last_updated=vibe.last_updated,
        signals=SignalsOut(**vibe.signals_dict()),
    )
