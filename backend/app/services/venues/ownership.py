# -*- coding: utf-8 -*-
"""Ownership lookups shared across serializers and the webhook dispatcher.

A venue is "verified" when at least one VenueClaim row exists for it with
status='verified' (the canonical post-approval state in this codebase).
"""
from __future__ import annotations

from functools import lru_cache
from typing import Iterable

from sqlalchemy.orm import Session

from app.models import VenueClaim
from datetime import datetime, timezone


def verified_venue_ids(db: Session) -> set[str]:
    """Return the set of venue ids that currently have an ACTIVE verified claim.
    Claims with expired ownership (`meta.ownership_expires_at` in the past) are
    treated as unverified so the public `is_verified` badge disappears when
    ownership lapses or is transferred/expired."""
    rows = (
        db.query(VenueClaim)
        .filter(VenueClaim.status == "verified")
        .all()
    )
    now = datetime.now(timezone.utc)
    out: set[str] = set()
    for c in rows:
        raw = (c.meta or {}).get("ownership_expires_at")
        if raw:
            try:
                exp = datetime.fromisoformat(raw)
                if exp <= now:
                    continue
            except Exception:
                pass
        out.add(c.venue_id)
    return out


def owner_claims_for_venue(db: Session, venue_id: str) -> list[VenueClaim]:
    """All verified claims for a venue (usually 0 or 1, but multi-claim safe)."""
    return (
        db.query(VenueClaim)
        .filter(VenueClaim.venue_id == venue_id, VenueClaim.status == "verified")
        .all()
    )


def claims_for_email(db: Session, email: str) -> list[VenueClaim]:
    """All verified claims held by this email (drives multi-venue ownership)."""
    return (
        db.query(VenueClaim)
        .filter(VenueClaim.email == email, VenueClaim.status == "verified")
        .order_by(VenueClaim.verified_at.desc())
        .all()
    )
