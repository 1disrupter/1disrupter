# -*- coding: utf-8 -*-
"""Tourist-Trap classifier.

Heuristic:
  • high Google busyness (>= 7) + low social (<= 4) + low votes (<= 4) -> tourist_trap
  • high social (>= 7) + high votes (>= 7) + moderate Google (4..7)    -> local_gem
  • otherwise                                                          -> neutral
"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Venue, VenueSignals

LABEL_TOURIST = "tourist_trap"
LABEL_GEM = "local_gem"
LABEL_NEUTRAL = "neutral"


def classify(signals: Optional[VenueSignals]) -> tuple[str, str]:
    """Return (label, reason) for one row."""
    if signals is None:
        return LABEL_NEUTRAL, "no external signals yet"

    g = float(signals.google_score or 0.0)
    s = float(signals.social_score or 0.0)
    v = float(signals.user_votes_score or 0.0)

    if g >= 7.0 and s <= 4.0 and v <= 4.0:
        return LABEL_TOURIST, f"busy online (google={g}) but quiet socially (social={s}) & votes low ({v})"
    if s >= 7.0 and v >= 7.0 and 4.0 <= g <= 7.0:
        return LABEL_GEM, f"locals love it (social={s}, votes={v}) with moderate busyness ({g})"
    return LABEL_NEUTRAL, "no strong pattern"


def classify_all(db: Session) -> List[dict]:
    rows = (
        db.query(Venue, VenueSignals)
        .outerjoin(VenueSignals, VenueSignals.venue_id == Venue.id)
        .all()
    )
    out = []
    for venue, sig in rows:
        label, reason = classify(sig)
        out.append({
            "venue_id": venue.id,
            "name": venue.name,
            "category": venue.category.value,
            "label": label,
            "reason": reason,
            "signals": {
                "google_score": round(float(sig.google_score), 2) if sig else 0.0,
                "social_score": round(float(sig.social_score), 2) if sig else 0.0,
                "user_votes_score": round(float(sig.user_votes_score), 2) if sig else 0.0,
            },
        })
    return out
