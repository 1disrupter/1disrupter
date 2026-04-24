# -*- coding: utf-8 -*-
"""Eventbrite adapter — real event-density score for tonight."""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

import requests

NAME = "eventbrite"
ENV_VAR = "EVENTBRITE_API_TOKEN"

logger = logging.getLogger("vibe2nite.providers.eventbrite")


def is_configured() -> bool:
    return bool(os.environ.get(ENV_VAR, "").strip())


async def fetch(venue) -> Optional[float]:
    token = os.environ.get(ENV_VAR, "").strip()
    if not token:
        return None
    now = datetime.now(timezone.utc)
    end = now + timedelta(hours=12)
    try:
        r = requests.get(
            "https://www.eventbriteapi.com/v3/events/search/",
            params={
                "location.latitude": venue.latitude,
                "location.longitude": venue.longitude,
                "location.within": "500m",
                "start_date.range_start": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "start_date.range_end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "expand": "venue",
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=4,
        )
        r.raise_for_status()
        data = r.json()
        count = len(data.get("events") or [])
        # 0..10 normalization: saturate at 5 events.
        return float(min(10.0, count * 2.0))
    except Exception as exc:  # pragma: no cover
        logger.debug("eventbrite fetch failed: %s", exc)
        return None
