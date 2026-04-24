# -*- coding: utf-8 -*-
"""AI Vibe Forecast routes (additive)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.forecast import predict_vibe

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("/{venue_id}", summary="3-hour AI forecast for a venue")
def venue_forecast(venue_id: str, refresh: bool = False, db: Session = Depends(get_db)):
    if refresh:
        from app.services.forecast import clear_cache
        clear_cache()
    try:
        return predict_vibe(db, venue_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="venue not found")
