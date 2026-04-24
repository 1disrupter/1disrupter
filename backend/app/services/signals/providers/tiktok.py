# -*- coding: utf-8 -*-
"""TikTok adapter — real fetch chain via the Research API.

Required env:
  TIKTOK_ACCESS_TOKEN   - research API bearer token

Required per-venue data:
  VenueProfile.tags.social_handles.tiktok

Returns None (fallback to stub) when prerequisites missing or API fails.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests

from app.services.signals.providers._handles import tiktok_handle

NAME = "tiktok"
ENV_VAR = "TIKTOK_ACCESS_TOKEN"
TT_URL = "https://open.tiktokapis.com/v2/research/video/query/"

logger = logging.getLogger("vibe2nite.providers.tiktok")


def is_configured() -> bool:
    return bool(os.environ.get(ENV_VAR, "").strip())


async def fetch(venue) -> Optional[float]:
    token = os.environ.get(ENV_VAR, "").strip()
    handle = tiktok_handle(venue)
    if not (token and handle):
        return None
    try:
        now = datetime.now(timezone.utc)
        start = (now - timedelta(days=7)).strftime("%Y%m%d")
        end = now.strftime("%Y%m%d")
        body = {
            "query": {"and": [{"operation": "EQ", "field_name": "username", "field_values": [handle]}]},
            "start_date": start,
            "end_date": end,
            "max_count": 50,
        }
        r = requests.post(
            TT_URL,
            json=body,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            params={"fields": "id,create_time"},
            timeout=5,
        )
        if not r.ok:
            return None
        videos = (r.json().get("data") or {}).get("videos") or []
        # Saturate at 20 videos in last 7d → 10.0
        return float(min(10.0, len(videos) / 2.0))
    except Exception as exc:  # pragma: no cover
        logger.debug("tiktok fetch failed: %s", exc)
        return None
