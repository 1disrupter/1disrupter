# -*- coding: utf-8 -*-
"""Time-of-day / day-of-week pattern signal.

Heuristic only — no external API required.

Curve:
  Weekend late nights (Fri/Sat 21:00-02:00) → 8.5..10
  Weekday prime-time (Wed/Thu 20:00-00:00)  → 6..8
  Afternoon                                  → 3..5
  Early morning (04-10)                      → 0..1.5
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from app.services.signals._common import clamp


def _hour_curve(hour: int) -> float:
    """Smooth 0..1 curve centred on 23:00 (peak nightlife)."""
    # Shift so that 23:00 -> 0, 05:00 -> 12 (farthest).
    dist = min(abs(hour - 23), abs(hour - 23 + 24), abs(hour - 23 - 24))
    # 0 -> 1 (peak), ~12 -> 0 (trough). Use cosine-ish fall off.
    return max(0.0, 1.0 - (dist / 8.0))


def _day_boost(weekday: int) -> float:
    # Monday=0 … Sunday=6
    return {
        0: -1.0,
        1: -1.0,
        2: -0.5,
        3: 0.5,
        4: 2.0,  # Fri
        5: 2.5,  # Sat
        6: 0.5,  # Sun
    }.get(weekday, 0.0)


async def get_time_pattern_score(venue, now: Optional[datetime] = None) -> float:
    """Return a 0–10 score based on day/hour nightlife patterns."""
    now = now or datetime.now(timezone.utc)
    base = _hour_curve(now.hour) * 9.0          # 0..9 peak from time-of-day
    base += _day_boost(now.weekday())           # -1 .. +2.5 from day-of-week
    return clamp(base)
