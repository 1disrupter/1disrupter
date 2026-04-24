# -*- coding: utf-8 -*-
"""Instagram Graph API adapter — real fetch chain when configured.

Required env:
  INSTAGRAM_ACCESS_TOKEN   - long-lived IG Graph token (page/business)
  INSTAGRAM_IG_USER_ID     - the IG business user id that can call hashtag search

Required per-venue data:
  VenueProfile.tags.social_handles.instagram (set via owner dashboard)

Chain:
  GET /ig_hashtag_search?user_id=...&q=<handle>        → hashtag id
  GET /{hashtag_id}/recent_media?user_id=...&limit=50  → count recent posts
Score = clamp((recent_post_count / 5) , 0, 10).

Returns None (falls back to stub) when any prerequisite is missing or fails.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

import requests

from app.services.signals.providers._handles import instagram_handle

NAME = "instagram"
ENV_VAR = "INSTAGRAM_ACCESS_TOKEN"
IG_GRAPH = "https://graph.facebook.com/v20.0"

logger = logging.getLogger("vibe2nite.providers.instagram")


def is_configured() -> bool:
    return bool(os.environ.get(ENV_VAR, "").strip())


async def fetch(venue) -> Optional[float]:
    token = os.environ.get(ENV_VAR, "").strip()
    ig_user = os.environ.get("INSTAGRAM_IG_USER_ID", "").strip()
    handle = instagram_handle(venue)
    if not (token and ig_user and handle):
        return None

    try:
        # 1) Resolve hashtag id (IG's hashtag search works on handles/names too).
        q = requests.get(
            f"{IG_GRAPH}/ig_hashtag_search",
            params={"user_id": ig_user, "q": handle, "access_token": token},
            timeout=4,
        )
        if not q.ok:
            return None
        data = q.json().get("data") or []
        if not data:
            return None
        hashtag_id = data[0].get("id")
        if not hashtag_id:
            return None

        # 2) Recent media velocity for that tag.
        r = requests.get(
            f"{IG_GRAPH}/{hashtag_id}/recent_media",
            params={
                "user_id": ig_user, "fields": "id,timestamp",
                "access_token": token, "limit": 50,
            },
            timeout=4,
        )
        if not r.ok:
            return None
        count = len((r.json().get("data") or []))
        # Saturate at 50 posts → 10.0
        score = min(10.0, count / 5.0)
        return float(score)
    except Exception as exc:  # pragma: no cover
        logger.debug("instagram fetch failed: %s", exc)
        return None
