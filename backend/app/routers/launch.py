# -*- coding: utf-8 -*-
"""Launch-mode routes (bulk city seed + per-venue onboarding) + push inbox."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Venue
from app.models.launch import NotificationLog
from app.services.launch import onboard_venue, seed_city, verify_admin_login
from app.services.notifications.push_engine import (
    broadcast_to_all, dispatch_spike_alerts, dispatch_tonight_hotspots,
    recent_for,
    send_daily_login, send_first_visit, send_offer_drop, send_tonight_hotspots,
    send_vibe_spike,
)

# ---------------------------------------------------------------------------
# City seed / onboard
# ---------------------------------------------------------------------------
city_router = APIRouter(prefix="/city", tags=["launch"])


class VenueSeedIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    category: str = Field("bar", pattern="^(bar|club|live_music)$")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    opening_hours: Optional[dict] = None
    music_type: Optional[str] = None
    price_level: Optional[int] = Field(None, ge=1, le=4)
    age_group: Optional[str] = None
    dress_code: Optional[str] = None
    photos: Optional[List[str]] = None


class CitySeedIn(BaseModel):
    city: str = Field(..., min_length=1, max_length=120)
    venues: List[VenueSeedIn]


@city_router.post("/seed", summary="Bulk upsert venues with launch-mode metadata")
def city_seed(payload: CitySeedIn, db: Session = Depends(get_db)):
    return seed_city(db, city_name=payload.city, venues=[v.model_dump() for v in payload.venues])


venues_router = APIRouter(prefix="/venues", tags=["launch"])


class OnboardIn(BaseModel):
    venue_id: str
    username: str = Field(..., min_length=3, max_length=60)
    password: str = Field(..., min_length=6, max_length=100)
    public_base_url: Optional[str] = None


@venues_router.post("/onboard", summary="Create a venue admin login + QR pack")
def onboard(payload: OnboardIn, db: Session = Depends(get_db)):
    try:
        return onboard_venue(
            db, venue_id=payload.venue_id, username=payload.username,
            password=payload.password, public_base_url=payload.public_base_url,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


class VenueLoginIn(BaseModel):
    username: str
    password: str


@venues_router.post("/login", summary="Venue-admin login (returns api_key)")
def venue_login(payload: VenueLoginIn, db: Session = Depends(get_db)):
    row = verify_admin_login(db, payload.username, payload.password)
    if row is None:
        raise HTTPException(status_code=401, detail="invalid credentials")
    return {"username": row.username, "venue_id": row.venue_id, "api_key": row.api_key}


# ---------------------------------------------------------------------------
# Push triggers (admin / debug) + inbox
# ---------------------------------------------------------------------------
triggers_router = APIRouter(prefix="/notifications", tags=["notifications"])


class TriggerIn(BaseModel):
    kind: str = Field(..., description="daily_login|first_visit_bonus|vibe_spike|offer_drop|tonight_hotspots")
    wallet_id: Optional[str] = Field(None, description="if omitted, broadcasts to ALL registered wallets")
    venue_id: Optional[str] = None
    offer_name: Optional[str] = None
    cost: Optional[int] = None
    offer_id: Optional[str] = None
    score: Optional[float] = None
    top_names: Optional[List[str]] = None


@triggers_router.post("/trigger/test", summary="Fire any push template manually (admin/debug)")
def trigger_test(payload: TriggerIn, db: Session = Depends(get_db)):
    kind = payload.kind

    def fan_out(send_fn, **kwargs) -> dict:
        if payload.wallet_id:
            return {"sent_to": 1, "result": send_fn(db, wallet_id=payload.wallet_id, **kwargs)}
        count = broadcast_to_all(db, send_fn=send_fn, **kwargs)
        return {"sent_to": count}

    if kind == "daily_login":
        return {"kind": kind, **fan_out(send_daily_login)}
    if kind == "first_visit_bonus":
        if not payload.venue_id:
            raise HTTPException(status_code=400, detail="venue_id required")
        return {"kind": kind, **fan_out(send_first_visit, venue_id=payload.venue_id)}
    if kind == "vibe_spike":
        if not payload.venue_id:
            raise HTTPException(status_code=400, detail="venue_id required")
        venue = db.get(Venue, payload.venue_id)
        if venue is None:
            raise HTTPException(status_code=404, detail="venue not found")
        return {"kind": kind, **fan_out(send_vibe_spike, venue=venue, new_score=float(payload.score or 9.0))}
    if kind == "offer_drop":
        if not payload.venue_id or not payload.offer_name or payload.cost is None:
            raise HTTPException(status_code=400, detail="venue_id, offer_name, cost required")
        venue = db.get(Venue, payload.venue_id)
        if venue is None:
            raise HTTPException(status_code=404, detail="venue not found")
        return {"kind": kind, **fan_out(
            send_offer_drop, venue=venue, offer_name=payload.offer_name,
            cost=int(payload.cost), offer_id=payload.offer_id or "",
        )}
    if kind == "tonight_hotspots":
        if payload.top_names:
            return {"kind": kind, **fan_out(send_tonight_hotspots, top_names=payload.top_names)}
        return {"kind": kind, "dispatched": dispatch_tonight_hotspots(db)}
    raise HTTPException(status_code=400, detail=f"unknown kind '{kind}'")


@triggers_router.post("/scan/spikes", summary="Run the vibe-spike detector now (async dispatch)")
def scan_spikes(background: BackgroundTasks):
    """Returns immediately; dispatch runs in the background via a fresh DB
    session so large token fan-outs don't hit ingress timeouts."""
    def _run_in_background() -> None:
        from app.core.database import SessionLocal
        s = SessionLocal()
        try:
            dispatch_spike_alerts(s)
        finally:
            s.close()

    background.add_task(_run_in_background)
    return {"status": "scheduled"}


# ---- Inbox ----
inbox_router = APIRouter(prefix="/notifications/inbox", tags=["notifications"])


@inbox_router.get("/{wallet_id}", summary="Last 20 notifications for a wallet")
def inbox(wallet_id: str, db: Session = Depends(get_db)):
    rows = recent_for(db, wallet_id, limit=20)
    return {
        "items": [
            {
                "id": r.id,
                "kind": r.kind,
                "title": r.title,
                "body": r.body,
                "data": r.data or {},
                "created_at": r.created_at.isoformat(),
            } for r in rows
        ]
    }
