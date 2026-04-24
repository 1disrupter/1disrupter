# -*- coding: utf-8 -*-
"""AI Vibe Forecast — 3-hour prediction from trajectory history + time-of-day.

Heuristic blend:
  baseline = last-hour moving average of venue_vibe_history
  momentum = slope of linear-fit over last 2h
  cycle    = hour-of-day factor (bars peak 22-01, live music 20-23)

  forecast = clamp(baseline + 1.5*momentum + cycle_boost, 0, 10)
  confidence = 1 - stdev/avg of recent 6 samples  (0..1)

5-minute in-memory cache keyed by venue_id.
"""
from __future__ import annotations

import math
import statistics
import time
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models import Venue, Vibe, VenueVibeHistory

_CACHE_TTL_S = 300
_cache: dict[str, tuple[float, dict]] = {}


def _cycle_boost(hour: int, category: str) -> float:
    """Simple hour-of-day curve, differentiated by venue type."""
    if category == "live_music":
        # peaks 20-23
        return 1.5 * math.exp(-((hour - 21.5) ** 2) / 4.0)
    # bars / clubs peak 22-01
    center = 23.0
    h = hour if hour >= 12 else hour + 24
    return 1.8 * math.exp(-((h - center) ** 2) / 6.0)


def _classify_trend(delta: float) -> str:
    if delta >= 0.6:
        return "rising"
    if delta <= -0.6:
        return "falling"
    if abs(delta) < 0.15 and delta > 0:
        return "peaking" if delta > 0 else "steady"
    return "steady"


def predict_vibe(db: Session, venue_id: str) -> dict:
    hit = _cache.get(venue_id)
    now_s = time.time()
    if hit and now_s - hit[0] < _CACHE_TTL_S:
        return {**hit[1], "cached": True}

    venue = db.get(Venue, venue_id)
    if venue is None:
        raise ValueError("venue not found")
    vibe = db.get(Vibe, venue_id)
    current_score = float(vibe.vibe_score or 0.0) if vibe else 0.0

    # Last 24h of trajectory
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    rows = (
        db.query(VenueVibeHistory)
        .filter(
            VenueVibeHistory.venue_id == venue_id,
            VenueVibeHistory.timestamp >= since,
        )
        .order_by(VenueVibeHistory.timestamp.asc())
        .all()
    )

    recent = [float(r.vibe_score or 0.0) for r in rows[-24:]] or [current_score]
    baseline = statistics.fmean(recent)

    # Linear-fit momentum over last 6 samples (~30 min at 5 min cadence)
    tail = recent[-6:] if len(recent) >= 6 else recent
    if len(tail) >= 2:
        xs = list(range(len(tail)))
        mean_x = sum(xs) / len(xs)
        mean_y = sum(tail) / len(tail)
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, tail))
        den = sum((x - mean_x) ** 2 for x in xs) or 1.0
        momentum = num / den
    else:
        momentum = 0.0

    # Hour-of-day cycle (UTC; callers can shift — keeps things deterministic)
    hour = datetime.now(timezone.utc).hour
    category = venue.category.value if hasattr(venue.category, "value") else str(venue.category)
    cycle = _cycle_boost(hour, category)

    forecast = baseline + 1.5 * momentum + cycle
    forecast = max(0.0, min(10.0, forecast))

    # Confidence: tighter dispersion → higher confidence. Bound 0..1.
    if len(recent) >= 3:
        stdev = statistics.pstdev(recent)
        confidence = max(0.0, min(1.0, 1.0 - stdev / 10.0))
    else:
        confidence = 0.3

    delta = forecast - current_score
    trend = _classify_trend(delta)
    # Upgrade to "peaking" if we're already near the top AND momentum is near zero.
    if current_score >= 8.5 and abs(momentum) < 0.1:
        trend = "peaking"

    payload = {
        "venue_id": venue_id,
        "current_score": round(current_score, 2),
        "forecast_score": round(forecast, 2),
        "trend": trend,
        "confidence": round(confidence, 2),
        "momentum": round(momentum, 3),
        "baseline": round(baseline, 2),
        "cycle_boost": round(cycle, 2),
        "horizon_hours": 3,
        "as_of": datetime.now(timezone.utc).isoformat(),
        "cached": False,
    }
    _cache[venue_id] = (now_s, payload)
    return payload


def clear_cache() -> int:
    n = len(_cache)
    _cache.clear()
    return n
