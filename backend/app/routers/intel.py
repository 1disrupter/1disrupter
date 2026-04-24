# -*- coding: utf-8 -*-
"""User Intelligence Layer routes — anonymous mobile signals + flow/trajectory."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Venue
from app.services.user_intel import (
    append_current_scores,
    compute_flow,
    detect_visits,
    get_trajectory,
    list_visits,
    record_ping,
)
from app.services.rewards.first_visit import check_in_and_reward, award_first_verified_visit

router = APIRouter(prefix="/intel", tags=["intel"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class PingIn(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    device_id: Optional[str] = Field(None, max_length=64)
    timestamp: Optional[datetime] = None


class PingOut(BaseModel):
    id: str
    timestamp: datetime


class VisitOut(BaseModel):
    id: str
    venue_id: str
    device_id: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class FlowOut(BaseModel):
    venue_id: str
    name: str
    flow: str
    pings_now: int
    pings_past: int


class TrajectoryPoint(BaseModel):
    timestamp: datetime
    vibe_score: float


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post("/ping", response_model=PingOut, summary="Record an anonymous location ping")
def create_ping(payload: PingIn, db: Session = Depends(get_db)) -> PingOut:
    ts = payload.timestamp or datetime.now(timezone.utc)
    row = record_ping(
        db, lat=payload.lat, lng=payload.lng, timestamp=ts, device_id=payload.device_id,
    )
    return PingOut(id=row.id, timestamp=row.timestamp)


@router.post("/visits/detect", summary="Run the venue-visit detector once")
def run_visit_detector(db: Session = Depends(get_db)):
    created = detect_visits(db)
    return {"created": created}


@router.get("/visits/{venue_id}", response_model=list[VisitOut], summary="Recent visits for a venue")
def venue_visits(
    venue_id: str,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    if not db.get(Venue, venue_id):
        raise HTTPException(status_code=404, detail="venue not found")
    return [VisitOut.model_validate(v) for v in list_visits(db, venue_id, limit=limit)]


@router.get("/flow", response_model=list[FlowOut], summary="Per-venue crowd flow (rising/falling/…)")
def flow(db: Session = Depends(get_db)):
    return [FlowOut(**r) for r in compute_flow(db)]


@router.get(
    "/trajectory/{venue_id}",
    response_model=list[TrajectoryPoint],
    summary="Vibe-score history points for a venue",
)
def trajectory(
    venue_id: str,
    hours: int = Query(6, ge=1, le=72),
    db: Session = Depends(get_db),
):
    if not db.get(Venue, venue_id):
        raise HTTPException(status_code=404, detail="venue not found")
    rows = get_trajectory(db, venue_id, hours=hours)
    return [TrajectoryPoint(timestamp=r.timestamp, vibe_score=r.vibe_score) for r in rows]


@router.post("/trajectory/snapshot", summary="Force-append a trajectory snapshot (admin/debug)")
def snapshot(db: Session = Depends(get_db)):
    return {"written": append_current_scores(db)}


# ---------------------------------------------------------------------------
# Iter 16 — visit check-in with first-verified-visit reward loop
# ---------------------------------------------------------------------------
class CheckInIn(BaseModel):
    venue_id: str
    device_id: str = Field(..., min_length=4, max_length=64)


@router.post("/visits/check-in", summary="Record a visit and evaluate the first-verified-visit reward")
def visits_check_in(payload: CheckInIn, db: Session = Depends(get_db)):
    if not db.get(Venue, payload.venue_id):
        raise HTTPException(status_code=404, detail="venue not found")
    return check_in_and_reward(db, venue_id=payload.venue_id, user_id=payload.device_id)


@router.post("/visits/{venue_id}/award-first", summary="Evaluate the first-visit reward without recording a new visit")
def visits_award_first(venue_id: str, device_id: str = Query(..., min_length=4, max_length=64), db: Session = Depends(get_db)):
    if not db.get(Venue, venue_id):
        raise HTTPException(status_code=404, detail="venue not found")
    return award_first_verified_visit(db, venue_id=venue_id, user_id=device_id)

