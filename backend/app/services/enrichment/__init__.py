# -*- coding: utf-8 -*-
"""Automatic venue-enrichment engine.

Pulls external signals (weather, events, travel-density, social proxies,
footfall) every 30 min via APScheduler + on-demand via
POST /api/intel/enrich/{venue_id}.

All providers degrade gracefully when API keys are missing — enrichment
never raises into the rest of the app. The combined signal bundle is
stored into `VenueIntel.signals` JSON + `last_enriched_at`.

Existing Signal-Engine / Vibe-Score / classifier logic is NOT modified.
This module only writes **optional inputs** that can be consumed later.
"""
from __future__ import annotations

import logging
import math
import random
import time
from datetime import datetime, timezone
from typing import Optional

import requests
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models import Venue, Vibe, VenueVibeHistory
from app.models.launch import VenueIntel, VenueProfile

logger = logging.getLogger("vibe2nite.enrichment")


# ---------------------------------------------------------------------------
# Providers (each returns a dict or None; never raises)
# ---------------------------------------------------------------------------
def _weather(lat: float, lng: float) -> Optional[dict]:
    key = (get_settings().__dict__.get("OPENWEATHER_API_KEY") or "").strip() \
        if hasattr(get_settings(), "__dict__") else ""
    # We don't add the env key to Settings — read directly from os.environ so we
    # don't force every installation to have it.
    import os
    key = os.environ.get("OPENWEATHER_API_KEY", "")
    if not key:
        return None
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat": lat, "lon": lng, "appid": key, "units": "metric"},
            timeout=5,
        )
        r.raise_for_status()
        d = r.json()
        return {
            "temp_c": float(d["main"]["temp"]),
            "feels_c": float(d["main"]["feels_like"]),
            "condition": d["weather"][0]["main"] if d.get("weather") else None,
            "wind_kmh": float(d["wind"]["speed"]) * 3.6 if d.get("wind") else None,
            "source": "openweathermap",
        }
    except Exception as exc:  # pragma: no cover
        logger.debug("weather provider failed: %s", exc)
        return None


def _events(venue: Venue) -> Optional[dict]:
    """Songkick/Bandsintown — stubbed until keys are provided. Deterministic
    per-venue count so tests can assert on it."""
    import os
    if os.environ.get("BANDSINTOWN_API_KEY") or os.environ.get("SONGKICK_API_KEY"):
        # Real integration placeholder — don't make uninvited network calls.
        return {"tonight_count": 0, "source": "bandsintown_pending"}
    # Deterministic stub — based on venue id hash → 0..3 events.
    seed = sum(ord(c) for c in venue.id) % 97
    return {"tonight_count": int(seed % 4), "source": "stub"}


def _travel_density(venue: Venue) -> Optional[dict]:
    """A tiny density proxy using OSRM isochrone would be ideal; we provide
    a fast stub so admins see a number even without keys."""
    # Higher near NYC centre (40.758,-73.985) — placeholder heuristic.
    d = math.hypot(venue.latitude - 40.758, venue.longitude + 73.985)
    density = max(0.0, min(1.0, 1.0 - d * 20))
    return {"density_index": round(density, 3), "source": "stub"}


def _social_engagement(venue: Venue) -> dict:
    """Instagram/TikTok engagement — stub. Deterministic 0..100 based on
    venue id + the current hour so we get movement across days."""
    hour = datetime.now(timezone.utc).hour
    seed = (sum(ord(c) for c in venue.id) + hour * 7) % 100
    return {"ig_score": seed, "tt_score": (seed * 3) % 100, "source": "stub"}


def _footfall_proxy(db: Session, venue: Venue) -> dict:
    """Lightweight footfall proxy — distinct visit count over last 2h."""
    from datetime import timedelta
    from app.models import VenueVisit
    since = datetime.now(timezone.utc) - timedelta(hours=2)
    visits = (
        db.query(VenueVisit)
        .filter(VenueVisit.venue_id == venue.id, VenueVisit.timestamp >= since)
        .all()
    )
    distinct = len({v.device_id for v in visits if v.device_id})
    return {
        "visits_2h": len(visits),
        "distinct_devices_2h": distinct,
        "source": "internal",
    }


# ---------------------------------------------------------------------------
# Derived optional inputs (for future consumers — never mutate vibe table)
# ---------------------------------------------------------------------------
def _derive_optional_inputs(db: Session, venue: Venue, signals: dict) -> dict:
    """Compute momentum / gem-score-delta / forecast-baseline hints.
    These are **optional** inputs any downstream consumer can merge in."""
    from datetime import timedelta
    since = datetime.now(timezone.utc) - timedelta(hours=1)
    history = (
        db.query(VenueVibeHistory)
        .filter(VenueVibeHistory.venue_id == venue.id,
                VenueVibeHistory.timestamp >= since)
        .order_by(VenueVibeHistory.timestamp.asc())
        .all()
    )
    if len(history) >= 2:
        start = float(history[0].vibe_score or 0.0)
        end = float(history[-1].vibe_score or 0.0)
        momentum = end - start
    else:
        momentum = 0.0

    events = signals.get("events") or {}
    tonight_count = int(events.get("tonight_count", 0) or 0)
    ig = (signals.get("social") or {}).get("ig_score", 0) or 0
    ff = (signals.get("footfall") or {}).get("distinct_devices_2h", 0) or 0

    return {
        "vibe_momentum_hint": round(float(momentum), 3),
        "forecast_baseline_hint": round(
            float((history[-1].vibe_score if history else (db.get(Vibe, venue.id).vibe_score if db.get(Vibe, venue.id) else 0.0)) or 0.0),
            2,
        ),
        "local_gem_hint": round(min(1.0, (ff / 10.0) + (ig / 500.0)), 3),
        "tourist_trap_hint": round(min(1.0, tonight_count / 5.0 + max(0.0, -momentum)), 3),
    }


# ---------------------------------------------------------------------------
# Main enrich
# ---------------------------------------------------------------------------
def enrich_venue(db: Session, venue_id: str, *, refresh: bool = False) -> dict:
    venue = db.get(Venue, venue_id)
    if venue is None:
        raise ValueError("venue not found")

    row = db.get(VenueIntel, venue_id)
    if row and not refresh and row.last_enriched_at:
        age = (datetime.now(timezone.utc) - row.last_enriched_at).total_seconds()
        if age < 60 * 25:  # honor 25-min soft cache unless refresh
            return {
                "venue_id": venue_id, "cached": True,
                "last_enriched_at": row.last_enriched_at.isoformat(),
                "signals": row.signals or {},
            }

    signals = {
        "weather":   _weather(venue.latitude, venue.longitude),
        "events":    _events(venue),
        "travel":    _travel_density(venue),
        "social":    _social_engagement(venue),
        "footfall":  _footfall_proxy(db, venue),
    }
    signals["derived"] = _derive_optional_inputs(db, venue, signals)

    now = datetime.now(timezone.utc)
    if row is None:
        row = VenueIntel(
            venue_id=venue_id, label="neutral", score=0.0, reason="enrichment only",
            signals=signals, last_enriched_at=now,
        )
        db.add(row)
    else:
        row.signals = signals
        row.last_enriched_at = now
    db.commit()

    return {
        "venue_id": venue_id, "cached": False,
        "last_enriched_at": now.isoformat(),
        "signals": signals,
    }


def enrich_all() -> dict:
    """Fan-out invoked by the scheduler — fresh session, never raises."""
    db = SessionLocal()
    ok, fail = 0, 0
    try:
        for v in db.query(Venue).all():
            try:
                enrich_venue(db, v.id)
                ok += 1
            except Exception as exc:  # pragma: no cover
                fail += 1
                logger.exception("enrich failed for %s: %s", v.id, exc)
    finally:
        db.close()
    return {"enriched": ok, "failed": fail}
