# -*- coding: utf-8 -*-
"""APScheduler background jobs.

Every 5 minutes, for every venue:
  1. compute signals via `compute_signals_for_venue`
  2. upsert a `venue_signals` row
  3. recompute `vibes.vibe_score` + `vibes.crowd_level` using the new
     signal-aware formula (additive — existing formula stays untouched).

The scheduler is started/stopped from the FastAPI lifespan in `app.main`.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.database import SessionLocal
from app.models import Venue, Vibe, VenueSignals
from app.services.scoring import calculate_vibe_score_from_signals, crowd_level_from_score
from app.services.signals import compute_signals_for_venue
from app.services.user_intel import append_current_scores, detect_visits
from app.services.ws_manager import manager as ws_manager

logger = logging.getLogger("vibe2nite.scheduler")

scheduler = AsyncIOScheduler(timezone="UTC")
REFRESH_MINUTES = 5

# Prevent overlap if a previous run is still in flight.
_refresh_lock = asyncio.Lock()


async def refresh_venue_signals(venue_id: str) -> dict:
    """Refresh a single venue. Used by the scheduler and admin trigger."""
    db = SessionLocal()
    try:
        venue = db.get(Venue, venue_id)
        if not venue:
            return {"venue_id": venue_id, "skipped": True}

        result = await compute_signals_for_venue(venue, db=db)

        row = db.query(VenueSignals).filter(VenueSignals.venue_id == venue.id).one_or_none()
        if row is None:
            row = VenueSignals(venue_id=venue.id)
            db.add(row)

        row.google_score = result["google"]
        row.social_score = result["social"]
        row.event_score = result["events"]
        row.time_score = result["time"]
        row.user_votes_score = result["votes"]
        row.updated_at = datetime.now(timezone.utc)

        # Fold into the existing Vibe row (additive; existing formula kept
        # available via compute_vibe_score). We use manual_score + venue_boost
        # from the existing Vibe record so admin-set values remain authoritative.
        vibe = db.get(Vibe, venue.id)
        if vibe is None:
            vibe = Vibe(venue_id=venue.id)
            db.add(vibe)

        new_score = calculate_vibe_score_from_signals(
            row, manual_score=vibe.manual_score, venue_boost=vibe.venue_boost
        )
        vibe.social_activity = row.social_score
        vibe.time_prediction = row.time_score
        # user_votes in Vibe stays driven by POST /feedback; mirror the derived
        # signal into the cached table only.
        vibe.vibe_score = new_score
        vibe.crowd_level = crowd_level_from_score(new_score)
        vibe.last_updated = datetime.now(timezone.utc)

        db.commit()
        # Broadcast live update to any WebSocket subscribers for this venue.
        try:
            event = {
                "type": "vibe_update",
                "venue_id": venue.id,
                "vibe_score": new_score,
                "crowd_level": vibe.crowd_level.value if hasattr(vibe.crowd_level, "value") else vibe.crowd_level,
                "external_signals": {
                    "google_score": row.google_score,
                    "social_score": row.social_score,
                    "event_score": row.event_score,
                    "time_score": row.time_score,
                    "user_votes_score": row.user_votes_score,
                },
                "last_updated": row.updated_at.isoformat(),
            }
            # Use the loop-aware dispatcher so POST /feedback (which uses its
            # own asyncio.run) still reaches sockets bound to the main loop.
            ws_manager.broadcast_sync(venue.id, event)
        except Exception:  # pragma: no cover
            pass
        return {"venue_id": venue.id, **result, "vibe_score": new_score}
    except Exception as exc:  # pragma: no cover - best-effort logging
        db.rollback()
        logger.exception("refresh_venue_signals failed for %s: %s", venue_id, exc)
        return {"venue_id": venue_id, "error": str(exc)}
    finally:
        db.close()


async def refresh_all_signals() -> dict:
    """Refresh every venue. Safe to call manually (admin endpoint)."""
    if _refresh_lock.locked():
        return {"status": "already_running"}
    async with _refresh_lock:
        db = SessionLocal()
        try:
            ids = [v.id for v in db.query(Venue.id).all()]
        finally:
            db.close()

        ok, errs = 0, 0
        for vid in ids:
            r = await refresh_venue_signals(vid)
            if "error" in r:
                errs += 1
            else:
                ok += 1

        # Trajectory snapshot + visit detection (additive, non-fatal on error).
        snap, visits = 0, 0
        db = SessionLocal()
        try:
            snap = append_current_scores(db)
            visits = detect_visits(db)
        except Exception as exc:  # pragma: no cover
            logger.exception("trajectory/visit side-jobs failed: %s", exc)
        finally:
            db.close()

        logger.info(
            "refresh_all_signals: %d ok, %d errors (of %d) | history=%d visits=%d",
            ok, errs, len(ids), snap, visits,
        )
        return {
            "status": "ok", "refreshed": ok, "errors": errs, "total": len(ids),
            "trajectory_points": snap, "visits_detected": visits,
        }


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.add_job(
        refresh_all_signals,
        trigger=IntervalTrigger(minutes=REFRESH_MINUTES),
        id="refresh_all_signals",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
        next_run_time=datetime.now(timezone.utc),  # run once at startup
    )
    scheduler.start()
    logger.info("Vibe2Nite scheduler started (interval=%s min)", REFRESH_MINUTES)


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Vibe2Nite scheduler stopped")
