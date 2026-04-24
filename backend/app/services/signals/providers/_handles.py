# -*- coding: utf-8 -*-
"""Helper: per-venue social handles stored on VenueProfile.tags.social_handles."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session


def _get_db() -> Session:
    from app.core.database import SessionLocal
    return SessionLocal()


def _handles_for(venue) -> dict:
    """Return {'instagram': '...', 'tiktok': '...'} if any, else {}."""
    try:
        db = _get_db()
        try:
            from app.models.launch import VenueProfile
            profile = db.get(VenueProfile, venue.id)
            if not profile or not profile.tags:
                return {}
            return (profile.tags or {}).get("social_handles") or {}
        finally:
            db.close()
    except Exception:
        return {}


def instagram_handle(venue) -> Optional[str]:
    return _handles_for(venue).get("instagram") or None


def tiktok_handle(venue) -> Optional[str]:
    return _handles_for(venue).get("tiktok") or None
