# -*- coding: utf-8 -*-
"""Pluggable real-provider adapters for the Signal Engine.

Each submodule exports two callables:
    is_configured() -> bool
    fetch(venue)    -> Optional[float]   # 0..10 or None when the provider
                                          # can't answer (missing key, error,
                                          # rate-limited). None signals the
                                          # caller to use its stub baseline.

All adapters:
  * read their API key via os.environ (no Settings coupling)
  * respect short timeouts and never raise into the Signal Engine
  * return `None` when unconfigured so existing stubs keep working
"""
from __future__ import annotations

import os
from typing import Callable, Iterable

from app.services.signals.providers import (
    google_places,
    instagram,
    tiktok,
    eventbrite,
    ticketmaster,
)


# Ordered lists — first provider in each category that returns a real number wins.
SOCIAL_PROVIDERS: Iterable = (instagram, tiktok)
EVENT_PROVIDERS:  Iterable = (ticketmaster, eventbrite)
BUSYNESS_PROVIDERS: Iterable = (google_places,)


def provider_status() -> list[dict]:
    """Shape for the admin 'Provider status' panel."""
    groups = [
        ("social",   SOCIAL_PROVIDERS),
        ("events",   EVENT_PROVIDERS),
        ("busyness", BUSYNESS_PROVIDERS),
    ]
    rows: list[dict] = []
    for category, mods in groups:
        for m in mods:
            rows.append({
                "category": category,
                "provider": m.NAME,
                "configured": bool(m.is_configured()),
                "env_var": m.ENV_VAR,
                "mode": "live" if m.is_configured() else "stub",
            })
    return rows


async def first_available(providers: Iterable, venue) -> float | None:
    """Try each provider in order; return the first real score, else None."""
    for m in providers:
        if not m.is_configured():
            continue
        try:
            val = await m.fetch(venue)
            if val is not None:
                return float(val)
        except Exception:
            # Defensive — providers never break the Signal Engine
            continue
    return None


__all__ = [
    "SOCIAL_PROVIDERS", "EVENT_PROVIDERS", "BUSYNESS_PROVIDERS",
    "provider_status", "first_available",
]
