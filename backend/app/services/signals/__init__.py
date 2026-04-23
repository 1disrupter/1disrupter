# -*- coding: utf-8 -*-
"""Signal Engine package.

Collects external / derived signals for each venue. Each module exposes a
single `get_<signal>_score(venue) -> float` coroutine returning a 0-10 score.

All integrations are currently STUBBED but deterministic per-venue so the
system "feels alive" — real API wiring can slot in later without touching
callers.
"""
from app.services.signals.signal_engine import compute_signals_for_venue  # noqa: F401
