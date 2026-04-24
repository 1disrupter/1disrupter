# -*- coding: utf-8 -*-
"""Instagram Graph API adapter (optional).

Relies on a long-lived page access token via IG Graph (Business API). When the
token isn't set the adapter reports 'not configured' and the signal engine
falls back to its deterministic stub.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

import requests

NAME = "instagram"
ENV_VAR = "INSTAGRAM_ACCESS_TOKEN"

logger = logging.getLogger("vibe2nite.providers.instagram")


def is_configured() -> bool:
    return bool(os.environ.get(ENV_VAR, "").strip())


async def fetch(venue) -> Optional[float]:
    """Return a 0..10 social-activity score.

    Without a venue-level IG handle we can only do a hashtag search; this is a
    safe placeholder that keeps the plumbing live. Owners who wire a real
    handle to each venue later can upgrade this adapter in place.
    """
    token = os.environ.get(ENV_VAR, "").strip()
    if not token:
        return None
    # Unknown handle → conservative "not enough data" response so we still
    # fall back to the stub cleanly rather than emitting noise.
    tag = "".join(c for c in (venue.name or "").lower() if c.isalnum())[:32]
    if not tag:
        return None
    try:
        # Step 1 – resolve hashtag id. (Requires ig_hashtag_search which needs an IG user id.)
        # Without an IG user id we can't complete the full chain; treat as "unconfigured for this deployment".
        # We keep the call out for observability — logged only.
        logger.debug("instagram.fetch requested for tag=%s (no user-id chain wired)", tag)
        return None
    except Exception as exc:  # pragma: no cover
        logger.debug("instagram fetch failed: %s", exc)
        return None
