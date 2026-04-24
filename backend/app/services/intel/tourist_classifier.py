# -*- coding: utf-8 -*-
"""Tourist-trap / local-gem classifier with persistence.

Inputs per venue:
  - tourist_ratio      : proxy from high google_score + low user_votes_score
  - price_level        : from VenueProfile (default 2)
  - volatility         : stdev of last 12 vibe-history samples
  - time_anomaly       : off-peak activity — high vibe in morning hours
  - repeat_visits      : distinct device_ids / total visits ratio

Score ∈ [-1, +1]:
  < -0.25 → "tourist_trap"
  >  0.25 → "local_gem"
  else    → "neutral"

Persists to venue_intel table (upsert).
"""
from __future__ import annotations

import logging
import statistics
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Venue, VenueSignals, VenueVibeHistory, VenueVisit
from app.models.launch import VenueIntel, VenueProfile

logger = logging.getLogger("vibe2nite.tourist_classifier")


def _volatility(samples: list[float]) -> float:
    if len(samples) < 2:
        return 0.0
    return statistics.pstdev(samples)


def classify_venue(db: Session, venue: Venue) -> dict:
    sig = db.query(VenueSignals).filter(VenueSignals.venue_id == venue.id).one_or_none()
    google = float(sig.google_score) if sig else 5.0
    votes = float(sig.user_votes_score) if sig else 5.0
    social = float(sig.social_score) if sig else 5.0

    # Tourist ratio proxy: high google, low user votes → tourist-heavy
    tourist_signal = (google - votes) / 10.0      # -1..1

    # Price level — treat high as tourist-bias, low as local-bias (additive small weight)
    profile = db.get(VenueProfile, venue.id)
    price = profile.price_level if profile else 2
    price_signal = (price - 2) / 4.0               # $$ → 0, $$$$ → 0.5

    # Volatility from last 12 vibe-history samples
    since = datetime.now(timezone.utc) - timedelta(hours=2)
    series = [
        float(r.vibe_score or 0.0)
        for r in db.query(VenueVibeHistory)
        .filter(
            VenueVibeHistory.venue_id == venue.id,
            VenueVibeHistory.timestamp >= since,
        )
        .order_by(VenueVibeHistory.timestamp.desc())
        .limit(12)
        .all()
    ]
    vol = _volatility(series)
    vol_signal = min(vol / 3.0, 1.0)               # high volatility → more tourist

    # Repeat-visit ratio from venue_visits
    visits = db.query(VenueVisit).filter(VenueVisit.venue_id == venue.id).all()
    if visits:
        distinct = len({v.device_id for v in visits if v.device_id})
        total = len(visits)
        repeat_ratio = 1.0 - (distinct / total) if total else 0.0
    else:
        repeat_ratio = 0.0
    repeat_signal = repeat_ratio                    # high repeats → local gem

    # Blend: positive = local gem, negative = tourist trap
    score = (
        -0.45 * tourist_signal      # high tourist_signal drags toward trap
        + 0.30 * repeat_signal      # loyal base pushes toward gem
        - 0.15 * vol_signal         # chaos = tourist-y
        - 0.10 * price_signal       # pricey = slight tourist-lean
        + 0.05 * ((social - 5.0) / 5.0)  # buzz on social — very small gem bias
    )
    score = max(-1.0, min(1.0, score))

    if score <= -0.25:
        label = "tourist_trap"
        reason = f"google {google:.1f} vs votes {votes:.1f}; volatility {vol:.2f}"
    elif score >= 0.25:
        label = "local_gem"
        reason = f"repeat-visit {repeat_ratio:.2f}; votes {votes:.1f}"
    else:
        label = "neutral"
        reason = "mixed signals"

    # Persist / upsert
    row = db.get(VenueIntel, venue.id)
    if row is None:
        row = VenueIntel(venue_id=venue.id, label=label, score=score, reason=reason)
        db.add(row)
    else:
        row.label = label
        row.score = score
        row.reason = reason
        row.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "venue_id": venue.id,
        "name": venue.name,
        "label": label,
        "score": round(score, 3),
        "reason": reason,
        "updated_at": row.updated_at.isoformat(),
    }


def classify_all(db: Session) -> List[dict]:
    return [classify_venue(db, v) for v in db.query(Venue).all()]


def get_flags(db: Session) -> List[dict]:
    """Return persisted labels, auto-classifying any missing rows."""
    rows = db.query(VenueIntel).all()
    known = {r.venue_id for r in rows}
    missing = [v for v in db.query(Venue).all() if v.id not in known]
    for v in missing:
        classify_venue(db, v)
    out = []
    for r in db.query(VenueIntel).all():
        out.append({
            "venue_id": r.venue_id,
            "label": r.label,
            "score": float(r.score),
            "reason": r.reason,
            "updated_at": r.updated_at.isoformat(),
        })
    return out


def local_gems(db: Session, limit: int = 10) -> List[dict]:
    """Return top local gems by (vibe_score * gem_score * loyalty)."""
    from app.models import Vibe
    rows = db.query(VenueIntel, Venue, Vibe).join(
        Venue, Venue.id == VenueIntel.venue_id,
    ).join(Vibe, Vibe.venue_id == Venue.id).all()

    scored = []
    for intel, venue, vibe in rows:
        if intel.label == "tourist_trap":
            continue
        # Loyalty: distinct devices / total visits (computed on the fly — small dataset)
        visits = db.query(VenueVisit).filter(VenueVisit.venue_id == venue.id).all()
        if visits:
            distinct = len({v.device_id for v in visits if v.device_id})
            total = len(visits)
            loyalty = 1.0 - (distinct / total) if total else 0.0
        else:
            loyalty = 0.0
        rank = float(vibe.vibe_score or 0.0) * (1.0 + float(intel.score)) * (1.0 + loyalty)
        scored.append((rank, intel, venue, vibe))

    scored.sort(key=lambda x: x[0], reverse=True)
    out = []
    for rank, intel, venue, vibe in scored[:limit]:
        out.append({
            "venue_id": venue.id,
            "name": venue.name,
            "category": venue.category.value if hasattr(venue.category, "value") else str(venue.category),
            "lat": venue.latitude,
            "lng": venue.longitude,
            "vibe_score": float(vibe.vibe_score or 0.0),
            "gem_score": float(intel.score),
            "label": intel.label,
            "rank": round(rank, 3),
        })
    return out
