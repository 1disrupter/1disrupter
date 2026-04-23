# -*- coding: utf-8 -*-
"""Live-music detection.

Simple deterministic heuristic today. Slots in Songkick / Bandsintown / IG
scraping later — callers see the same response shape.

A venue is flagged as "live tonight" when either:
  • its category is `live_music` AND its event_score >= 3.0, OR
  • event_score >= 6.5 for any category (a bar/club running a DJ/band night).

Confidence in [0,1] is linear on event_score, scaled by category prior.
"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Venue, Vibe, VenueSignals
from app.models.venue import VenueCategory

CATEGORY_PRIOR = {
    VenueCategory.live_music: 1.00,
    VenueCategory.club: 0.70,
    VenueCategory.bar: 0.45,
}


def _flag_for(venue: Venue, signals: Optional[VenueSignals]) -> tuple[bool, float, str]:
    evt = float(signals.event_score or 0.0) if signals else 0.0
    cat = venue.category
    prior = CATEGORY_PRIOR.get(cat, 0.4)

    if cat == VenueCategory.live_music and evt >= 3.0:
        reason = "category=live_music + confirmed event signal"
        flagged = True
    elif evt >= 6.5:
        reason = "strong event signal"
        flagged = True
    else:
        reason = "no credible live-music signal"
        flagged = False

    confidence = round(min(1.0, (evt / 10.0) * prior + (0.25 if flagged else 0.0)), 3)
    return flagged, confidence, reason


def detect_live_music(db: Session, only_flagged: bool = True) -> List[dict]:
    rows = (
        db.query(Venue, Vibe, VenueSignals)
        .outerjoin(Vibe, Vibe.venue_id == Venue.id)
        .outerjoin(VenueSignals, VenueSignals.venue_id == Venue.id)
        .all()
    )
    out: List[dict] = []
    for venue, vibe, sig in rows:
        flagged, confidence, reason = _flag_for(venue, sig)
        if only_flagged and not flagged:
            continue
        out.append({
            "venue_id": venue.id,
            "name": venue.name,
            "category": venue.category.value,
            "lat": venue.latitude,
            "lng": venue.longitude,
            "live_music": flagged,
            "confidence": confidence,
            "event_score": round(float(sig.event_score) if sig else 0.0, 2),
            "vibe_score": round(float(vibe.vibe_score) if vibe else 0.0, 2),
            "reason": reason,
        })
    # Best candidates first
    out.sort(key=lambda x: (x["confidence"], x["event_score"]), reverse=True)
    return out
