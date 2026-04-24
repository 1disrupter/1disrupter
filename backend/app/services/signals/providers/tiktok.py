# -*- coding: utf-8 -*-
"""TikTok adapter (optional).

TikTok does not offer a public business search endpoint; most integrators go
through TikTok's research API (approval required). Until then, this adapter is
gated behind TIKTOK_ACCESS_TOKEN and returns None, letting the signal engine
fall back to its stub.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

NAME = "tiktok"
ENV_VAR = "TIKTOK_ACCESS_TOKEN"

logger = logging.getLogger("vibe2nite.providers.tiktok")


def is_configured() -> bool:
    return bool(os.environ.get(ENV_VAR, "").strip())


async def fetch(venue) -> Optional[float]:
    token = os.environ.get(ENV_VAR, "").strip()
    if not token:
        return None
    # Real integration lands when TikTok research API access is approved.
    logger.debug("tiktok.fetch stub-pass-through (approval pending)")
    return None
