# -*- coding: utf-8 -*-
"""P4 — OSM import + enrichment + AI discovery routes (all additive)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.ai_discovery import (
    approve_candidate, detect_closed_venues, detect_trending_venues,
    discover_new_venues, reject_candidate,
)
from app.services.enrichment import enrich_all, enrich_venue
from app.services.osm_import import import_osm, preview


# ---------------------------------------------------------------------------
# OSM import
# ---------------------------------------------------------------------------
osm_router = APIRouter(prefix="/import", tags=["osm"])


class BBoxIn(BaseModel):
    lat_min: float = Field(..., ge=-90, le=90)
    lat_max: float = Field(..., ge=-90, le=90)
    lon_min: float = Field(..., ge=-180, le=180)
    lon_max: float = Field(..., ge=-180, le=180)


class OsmImportIn(BaseModel):
    city: Optional[str] = Field(None, min_length=1, max_length=120)
    bbox: Optional[BBoxIn] = None
    overwrite: bool = False
    limit: int = Field(500, ge=1, le=2000)
    dry_run: bool = Field(False, description="Preview only — no DB writes.")


@osm_router.post("/osm", summary="Import venues from OpenStreetMap (city OR bbox)")
def osm_import(payload: OsmImportIn, db: Session = Depends(get_db)):
    if not payload.city and not payload.bbox:
        raise HTTPException(status_code=400, detail="city or bbox required")
    bbox = None
    if payload.bbox is not None:
        bbox = (payload.bbox.lat_min, payload.bbox.lat_max, payload.bbox.lon_min, payload.bbox.lon_max)
    try:
        if payload.dry_run:
            return preview(city=payload.city, bbox=bbox, limit=payload.limit)
        return import_osm(
            db, city=payload.city, bbox=bbox, overwrite=payload.overwrite,
            limit=payload.limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=502, detail=f"osm fetch failed: {exc}")


# ---------------------------------------------------------------------------
# Enrichment
# ---------------------------------------------------------------------------
enrich_router = APIRouter(prefix="/intel", tags=["enrichment"])


@enrich_router.post("/enrich/{venue_id}", summary="Enrich one venue immediately")
def enrich_one(
    venue_id: str,
    refresh: bool = Query(True, description="Ignore 25-min soft cache"),
    db: Session = Depends(get_db),
):
    try:
        return enrich_venue(db, venue_id, refresh=refresh)
    except ValueError:
        raise HTTPException(status_code=404, detail="venue not found")


@enrich_router.post("/enrich/all/run", summary="Run enrichment for every venue (background)")
def enrich_everything(background: BackgroundTasks):
    background.add_task(enrich_all)
    return {"status": "scheduled"}


@enrich_router.get("/enrich/{venue_id}", summary="Read the last-enriched signals for a venue")
def read_enrichment(venue_id: str, db: Session = Depends(get_db)):
    from app.models.launch import VenueIntel
    row = db.get(VenueIntel, venue_id)
    if row is None or row.last_enriched_at is None:
        raise HTTPException(status_code=404, detail="no enrichment yet")
    return {
        "venue_id": venue_id,
        "last_enriched_at": row.last_enriched_at.isoformat(),
        "signals": row.signals or {},
        "label": row.label,
        "score": float(row.score),
    }


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------
discovery_router = APIRouter(prefix="/discovery", tags=["discovery"])


@discovery_router.get("/new", summary="Candidate new venues in a city (from OSM)")
def new_venues(city: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    return discover_new_venues(db, city)


@discovery_router.get("/closed", summary="Candidate closed/inactive venues")
def closed_venues(city: str = Query(...), db: Session = Depends(get_db)):
    return detect_closed_venues(db, city)


@discovery_router.get("/trending", summary="Trending venues by multi-signal surge")
def trending_venues(city: str = Query(""), limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    return detect_trending_venues(db, city, limit=limit)


class CandidateActionIn(BaseModel):
    candidate_id: str


@discovery_router.post("/approve", summary="Approve a candidate (creates the live venue if kind=new)")
def approve(payload: CandidateActionIn, db: Session = Depends(get_db)):
    try:
        return approve_candidate(db, payload.candidate_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@discovery_router.post("/reject", summary="Reject a candidate")
def reject(payload: CandidateActionIn, db: Session = Depends(get_db)):
    try:
        return reject_candidate(db, payload.candidate_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
