# -*- coding: utf-8 -*-
"""Ticketmaster Discovery adapter — real event-density score for tonight."""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

import requests

NAME = "ticketmaster"
ENV_VAR = "TICKETMASTER_API_KEY"

logger = logging.getLogger("vibe2nite.providers.ticketmaster")


def is_configured() -> bool:
    return bool(os.environ.get(ENV_VAR, "").strip())


async def fetch(venue) -> Optional[float]:
    key = os.environ.get(ENV_VAR, "").strip()
    if not key:
        return None
    now = datetime.now(timezone.utc)
    end = now + timedelta(hours=12)
    try:
        r = requests.get(
            "https://app.ticketmaster.com/discovery/v2/events.json",
            params={
                "apikey": key,
                "latlong": f"{venue.latitude},{venue.longitude}",
                "radius": 1,          # 1 km
                "unit": "km",
                "startDateTime": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "endDateTime": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "size": 20,
            },
            timeout=4,
        )
        r.raise_for_status()
        data = r.json()
        count = int((data.get("page") or {}).get("totalElements") or 0)
        return float(min(10.0, count * 2.0))
    except Exception as exc:  # pragma: no cover
        logger.debug("ticketmaster fetch failed: %s", exc)
        return None
