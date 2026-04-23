# -*- coding: utf-8 -*-
"""Shared helpers for stubbed signal modules.

Stubs are deterministic per-venue (hash of venue.id + day) plus small live
noise driven by the current minute — so the dashboard feels alive while we
wait for the real integrations.
"""
from __future__ import annotations

import hashlib
import math
from datetime import datetime, timezone


def clamp(value: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return round(max(lo, min(hi, float(value))), 2)


def _hash_float(*parts: str) -> float:
    """Deterministic 0..1 float derived from the given string parts."""
    h = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def baseline_for(venue, salt: str, *, low: float = 2.0, high: float = 9.0) -> float:
    """Stable baseline in [low, high] unique to (venue, salt, today)."""
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    v = _hash_float(str(getattr(venue, "id", "?")), salt, day)
    return low + v * (high - low)


def live_jitter(amplitude: float = 0.6) -> float:
    """Small oscillation so consecutive scheduler runs show movement."""
    now = datetime.now(timezone.utc)
    t = now.minute * 60 + now.second
    return amplitude * math.sin(2 * math.pi * (t % 300) / 300.0)
