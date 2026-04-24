# -*- coding: utf-8 -*-
"""Launch-mode service — bulk venue seed + per-venue onboarding + QR generation."""
from __future__ import annotations

import base64
import hashlib
import io
import logging
import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional

import qrcode
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Venue, Vibe
from app.models.launch import VenueAdmin, VenueProfile
from app.models.venue import VenueCategory

logger = logging.getLogger("vibe2nite.launch")


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------
def _hash_password(password: str) -> str:
    """PBKDF2 hash (stdlib — no extra deps, good enough for MVP venue admins)."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return f"pbkdf2_sha256${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt_hex, digest_hex = stored.split("$", 2)
        if scheme != "pbkdf2_sha256":
            return False
        salt = bytes.fromhex(salt_hex)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
        return secrets.compare_digest(digest.hex(), digest_hex)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Bulk city seed
# ---------------------------------------------------------------------------
def seed_city(db: Session, *, city_name: str, venues: list[dict]) -> dict:
    """Bulk upsert venues + profiles. Each item may contain:
       { name, category, latitude, longitude, opening_hours, music_type,
         price_level, age_group, dress_code, photos }

    Existing venues with the same (name, city) won't be duplicated —
    match is by name (case-insensitive). Returns counts."""
    created, updated = 0, 0
    for raw in venues:
        try:
            name = str(raw["name"]).strip()
            existing = (
                db.query(Venue)
                .filter(Venue.name.ilike(name))
                .one_or_none()
            )
            if existing is None:
                cat = raw.get("category", "bar")
                v = Venue(
                    name=name,
                    category=VenueCategory(cat) if not isinstance(cat, VenueCategory) else cat,
                    latitude=float(raw["latitude"]),
                    longitude=float(raw["longitude"]),
                )
                db.add(v)
                db.flush()
                db.add(Vibe(venue_id=v.id))
                existing = v
                created += 1
            else:
                updated += 1

            # Upsert profile (additive — only writes fields that were provided)
            profile = db.get(VenueProfile, existing.id)
            if profile is None:
                profile = VenueProfile(venue_id=existing.id)
                db.add(profile)
            if "opening_hours" in raw:
                profile.opening_hours = dict(raw["opening_hours"] or {})
            if "music_type" in raw:
                profile.music_type = str(raw["music_type"] or "")
            if "price_level" in raw and raw["price_level"] is not None:
                profile.price_level = int(raw["price_level"])
            if "age_group" in raw:
                profile.age_group = str(raw["age_group"] or "")
            if "dress_code" in raw:
                profile.dress_code = str(raw["dress_code"] or "")
            if "photos" in raw:
                profile.photos = list(raw["photos"] or [])
            profile.updated_at = datetime.now(timezone.utc)
        except Exception as exc:  # pragma: no cover
            logger.exception("seed_city failed for %s: %s", raw, exc)

    db.commit()
    return {"city": city_name, "created": created, "updated": updated, "total": len(venues)}


# ---------------------------------------------------------------------------
# Venue onboarding
# ---------------------------------------------------------------------------
def _qr_png_data_url(payload: str) -> str:
    img = qrcode.make(payload, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def onboard_venue(
    db: Session, *, venue_id: str, username: str, password: str,
    public_base_url: Optional[str] = None,
) -> dict:
    venue = db.get(Venue, venue_id)
    if venue is None:
        raise ValueError("venue not found")
    if not username or not password or len(password) < 6:
        raise ValueError("invalid username/password")

    existing = db.get(VenueAdmin, username)
    if existing is not None:
        raise ValueError("username taken")

    api_key = secrets.token_urlsafe(32)
    row = VenueAdmin(
        username=username,
        venue_id=venue.id,
        password_hash=_hash_password(password),
        api_key=api_key,
    )
    db.add(row)
    db.commit()

    base = (public_base_url or "").rstrip("/") or "https://vibe2nite.app"
    qrs = {
        "check_in":      _qr_png_data_url(f"{base}/v/{venue.id}?action=check_in"),
        "feedback":      _qr_png_data_url(f"{base}/v/{venue.id}?action=feedback"),
        "follow_venue":  _qr_png_data_url(f"{base}/v/{venue.id}?action=follow"),
    }
    return {
        "venue_id": venue.id,
        "username": username,
        "api_key": api_key,
        "qr_codes": qrs,
    }


def verify_admin_login(db: Session, username: str, password: str) -> Optional[VenueAdmin]:
    row = db.get(VenueAdmin, username)
    if row is None or not verify_password(password, row.password_hash):
        return None
    return row
