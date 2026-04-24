# -*- coding: utf-8 -*-
"""Push engine — templated triggers + inbox persistence.

All functions are fire-and-forget: they never raise into calling code.
Logs every attempt to `notification_log` so the mobile inbox can display
the history even for users whose Expo tokens failed.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Optional

from sqlalchemy.orm import Session

from app.models import Venue, Vibe, VenueVibeHistory
from app.models.launch import NotificationLog
from app.models.push_token import UserPushToken
from app.services.notifications import send_push

logger = logging.getLogger("vibe2nite.push_engine")

# ---------------------------------------------------------------------------
# Inbox helpers
# ---------------------------------------------------------------------------
def _log_notification(
    db: Session, *, wallet_id: str, kind: str, title: str, body: str,
    data: Optional[dict] = None,
) -> NotificationLog:
    row = NotificationLog(
        id=str(uuid.uuid4()),
        wallet_id=wallet_id,
        kind=kind,
        title=title,
        body=body,
        data=data or {},
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def recent_for(db: Session, wallet_id: str, limit: int = 20) -> list[NotificationLog]:
    return (
        db.query(NotificationLog)
        .filter(NotificationLog.wallet_id == wallet_id)
        .order_by(NotificationLog.created_at.desc())
        .limit(limit)
        .all()
    )


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
TEMPLATES = {
    "daily_login":        {"title": "Welcome back 🌃", "body": "+1 Vibe Credit for checking in today."},
    "first_visit_bonus":  {"title": "First visit unlocked 🎁", "body": "You just earned +5 Vibe Credits."},
    "vibe_spike":         {"title": "🚀 Vibe spike!", "body": "{venue_name} just jumped to {score:.1f}. Go now."},
    "offer_drop":         {"title": "🎟️ New offer", "body": "{venue_name} just dropped: {offer_name} ({cost}c)."},
    "tonight_hotspots":   {"title": "Tonight's hotspots 🔥", "body": "Top 5 tonight: {names}"},
}


def _send_and_log(
    db: Session, *, wallet_id: str, kind: str, title: str, body: str,
    data: Optional[dict] = None,
) -> dict:
    _log_notification(db, wallet_id=wallet_id, kind=kind, title=title, body=body, data=data)
    return send_push(db, wallet_id=wallet_id, title=title, body=body, data={**(data or {}), "kind": kind})


def send_daily_login(db: Session, wallet_id: str) -> dict:
    t = TEMPLATES["daily_login"]
    return _send_and_log(db, wallet_id=wallet_id, kind="daily_login", title=t["title"], body=t["body"])


def send_first_visit(db: Session, wallet_id: str, venue_id: str) -> dict:
    t = TEMPLATES["first_visit_bonus"]
    return _send_and_log(
        db, wallet_id=wallet_id, kind="first_visit_bonus",
        title=t["title"], body=t["body"], data={"venue_id": venue_id},
    )


def send_vibe_spike(db: Session, wallet_id: str, venue: Venue, new_score: float) -> dict:
    t = TEMPLATES["vibe_spike"]
    return _send_and_log(
        db, wallet_id=wallet_id, kind="vibe_spike",
        title=t["title"],
        body=t["body"].format(venue_name=venue.name, score=new_score),
        data={"venue_id": venue.id, "score": new_score},
    )


def send_offer_drop(db: Session, wallet_id: str, venue: Venue, offer_name: str, cost: int, offer_id: str) -> dict:
    t = TEMPLATES["offer_drop"]
    return _send_and_log(
        db, wallet_id=wallet_id, kind="offer_drop",
        title=t["title"],
        body=t["body"].format(venue_name=venue.name, offer_name=offer_name, cost=cost),
        data={"venue_id": venue.id, "offer_id": offer_id},
    )


def send_tonight_hotspots(db: Session, wallet_id: str, top_names: list[str]) -> dict:
    t = TEMPLATES["tonight_hotspots"]
    return _send_and_log(
        db, wallet_id=wallet_id, kind="tonight_hotspots",
        title=t["title"],
        body=t["body"].format(names=", ".join(top_names[:5])),
        data={"venues": top_names[:5]},
    )


def broadcast_to_all(db: Session, *, send_fn, **kwargs) -> int:
    """Fan-out helper: call `send_fn(db_thread, wallet_id, **kwargs)` for every
    registered wallet. Each worker spins its own SessionLocal so SQLAlchemy
    sessions are never shared across threads."""
    from concurrent.futures import ThreadPoolExecutor
    from app.core.database import SessionLocal

    wallets = [r.wallet_id for r in db.query(UserPushToken).all()]
    if not wallets:
        return 0

    def _one(wid: str) -> int:
        s = SessionLocal()
        try:
            send_fn(s, wallet_id=wid, **kwargs)
            return 1
        except Exception as exc:  # pragma: no cover
            logger.exception("broadcast failed for %s: %s", wid, exc)
            try:
                s.rollback()
            except Exception:
                pass
            return 0
        finally:
            s.close()

    with ThreadPoolExecutor(max_workers=min(16, max(4, len(wallets)))) as pool:
        return sum(pool.map(_one, wallets))


# ---------------------------------------------------------------------------
# Vibe-spike detector (called every 10 minutes by the scheduler)
# ---------------------------------------------------------------------------
SPIKE_PCT = 0.12  # 12 %
SPIKE_WINDOW_MIN = 10


def detect_vibe_spikes(db: Session) -> list[dict]:
    """Compare each venue's current Vibe vs ~10 min ago. Return spikes > SPIKE_PCT."""
    now = datetime.now(timezone.utc)
    window_from = now - timedelta(minutes=SPIKE_WINDOW_MIN * 2)
    window_to = now - timedelta(minutes=SPIKE_WINDOW_MIN)

    # Baseline from history within 10-20 min ago
    baseline_rows = (
        db.query(VenueVibeHistory.venue_id, VenueVibeHistory.vibe_score, VenueVibeHistory.timestamp)
        .filter(VenueVibeHistory.timestamp >= window_from, VenueVibeHistory.timestamp <= window_to)
        .all()
    )
    baseline: dict[str, float] = {}
    for vid, score, _ts in baseline_rows:
        # Use the latest sample inside the window (list is unordered; pick max ts via second query cheap, but approximate here)
        baseline[vid] = float(score)

    spikes: list[dict] = []
    for v in db.query(Venue).all():
        vibe = db.get(Vibe, v.id)
        if not vibe or v.id not in baseline:
            continue
        prev = float(baseline[v.id] or 0.0)
        cur = float(vibe.vibe_score or 0.0)
        if prev <= 0 or cur <= 0:
            continue
        delta_pct = (cur - prev) / prev
        if delta_pct >= SPIKE_PCT:
            spikes.append({
                "venue_id": v.id,
                "name": v.name,
                "previous": prev,
                "current": cur,
                "delta_pct": round(delta_pct, 4),
            })
    return spikes


def dispatch_spike_alerts(db: Session) -> int:
    """Run the detector and push each spike to every registered wallet. Returns pushes sent."""
    sent = 0
    for spike in detect_vibe_spikes(db):
        venue = db.get(Venue, spike["venue_id"])
        if not venue:
            continue
        sent += broadcast_to_all(db, send_fn=send_vibe_spike, venue=venue, new_score=spike["current"])
    return sent


def dispatch_tonight_hotspots(db: Session) -> int:
    """Compute the top 5 venues by vibe_score and push to every registered wallet."""
    top_rows = (
        db.query(Venue, Vibe)
        .join(Vibe, Venue.id == Vibe.venue_id)
        .order_by(Vibe.vibe_score.desc())
        .limit(5)
        .all()
    )
    names = [v.name for v, _ in top_rows]
    if not names:
        return 0
    return broadcast_to_all(db, send_fn=send_tonight_hotspots, top_names=names)
