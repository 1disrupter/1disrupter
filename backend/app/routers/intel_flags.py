# -*- coding: utf-8 -*-
"""Intel flags + local gems (additive — separate from legacy /vibes/tourist-flags)."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.intel import classify_all, get_flags, local_gems

router = APIRouter(prefix="/intel", tags=["intel"])


@router.get("/tourist-flags", summary="Per-venue tourist-trap / local-gem classification")
def tourist_flags(db: Session = Depends(get_db)):
    return {"items": get_flags(db)}


@router.post("/tourist-flags/refresh", summary="Re-classify every venue")
def refresh_flags(db: Session = Depends(get_db)):
    return {"items": classify_all(db)}


@router.get("/local-gems", summary="Top local gems (ranked by vibe x gem x loyalty)")
def gems(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    return {"items": local_gems(db, limit=limit)}
