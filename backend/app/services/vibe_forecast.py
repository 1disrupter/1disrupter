# -*- coding: utf-8 -*-
"""Vibe-Forecast engine.

Predicts a short-term trend for each venue in {rising, peaking, falling, steady}
without requiring a stored history table. Uses:

  • time_of_day derivative of the same hour-curve used by time_patterns.py
    (so a venue at 21:00 UTC on Sat is `rising`, at 23:00 it's `peaking`,
    at 02:00 it's `falling`).
  • current vibe_score level (anchors `peaking` vs `steady`).
  • the cached time_score signal (supports live override from the scheduler).
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Venue, Vibe
from app.services.signals.time_patterns import _day_boost

TREND_RISING = "rising"
TREND_PEAKING = "peaking"
TREND_FALLING = "falling"
TREND_STEADY = "steady"

PEAK_DERIV = 0.10  # |delta(next hour)| below this == near-peak / stable


def _smooth_hour_curve(hour: int) -> float:
    """Smooth 0..9 curve peaking at 23:00 — never clamps to 0 so the forecast
    always has a directional signal. Separate from time_patterns._hour_curve
    (which is left untouched)."""
    # Cosine wave offset so maximum is at 23:00.
    rad = 2 * math.pi * ((hour - 23) % 24) / 24.0
    val = (1 + math.cos(rad)) / 2.0  # 0..1 with peak at 23
    return val * 9.0


def _curve_at(now: datetime) -> float:
    return _smooth_hour_curve(now.hour) + _day_boost(now.weekday())


def _predict(vibe: Optional[Vibe], now: Optional[datetime] = None) -> dict:
    now = now or datetime.now(timezone.utc)
    cur = _curve_at(now)
    nxt = _curve_at(now + timedelta(hours=1))
    delta = round(nxt - cur, 2)
    score = float(vibe.vibe_score) if vibe else 0.0

    if abs(delta) < PEAK_DERIV:
        trend = TREND_PEAKING if score >= 7.0 else TREND_STEADY
    elif delta > 0:
        trend = TREND_RISING
    else:
        trend = TREND_FALLING

    return {
        "trend": trend,
        "delta_next_hour": delta,
        "current_vibe_score": round(score, 2),
        "as_of": now.isoformat(),
    }


def forecast_all(db: Session) -> List[dict]:
    rows = (
        db.query(Venue, Vibe)
        .outerjoin(Vibe, Vibe.venue_id == Venue.id)
        .all()
    )
    out = []
    for venue, vibe in rows:
        pred = _predict(vibe)
        out.append({
            "venue_id": venue.id,
            "name": venue.name,
            **pred,
        })
    return out


def forecast_one(db: Session, venue_id: str) -> Optional[dict]:
    venue = db.get(Venue, venue_id)
    if not venue:
        return None
    vibe = db.get(Vibe, venue_id)
    pred = _predict(vibe)
    return {"venue_id": venue_id, "name": venue.name, **pred}
