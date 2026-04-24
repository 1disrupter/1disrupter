# -*- coding: utf-8 -*-
"""AI-based venue discovery.

Three detectors produce *candidates* that admins must approve before they
become live venues. Nothing auto-inserts into the `venues` table.
"""
from __future__ import annotations

import logging
import math
import statistics
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Venue, Vibe, VenueVibeHistory
from app.models.discovery import VenueDiscoveryCandidate
from app.models.launch import VenueIntel, VenueProfile
from app.services.osm_import import preview as osm_preview

logger = logging.getLogger("vibe2nite.discovery")


# ---------------------------------------------------------------------------
# Candidate upsert helpers
# ---------------------------------------------------------------------------
def _upsert_candidate(
    db: Session, *, city: str, kind: str, name: str, lat: float, lng: float,
    confidence: float, reason: str, source: str, extra: Optional[dict] = None,
) -> VenueDiscoveryCandidate:
    existing = (
        db.query(VenueDiscoveryCandidate)
        .filter(
            VenueDiscoveryCandidate.city == city,
            VenueDiscoveryCandidate.kind == kind,
            VenueDiscoveryCandidate.name == name,
        )
        .one_or_none()
    )
    if existing is None:
        existing = VenueDiscoveryCandidate(
            id=str(uuid.uuid4()),
            city=city, kind=kind, name=name, lat=lat, lng=lng,
            confidence=confidence, reason=reason, source=source, extra=extra or {},
        )
        db.add(existing)
    else:
        existing.confidence = confidence
        existing.reason = reason
        existing.extra = extra or {}
    db.commit()
    return existing


def _list_pending(db: Session, city: str, kind: str) -> list[dict]:
    rows = (
        db.query(VenueDiscoveryCandidate)
        .filter(
            VenueDiscoveryCandidate.city == city,
            VenueDiscoveryCandidate.kind == kind,
            VenueDiscoveryCandidate.status == "pending",
        )
        .order_by(VenueDiscoveryCandidate.confidence.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "name": r.name,
            "lat": r.lat,
            "lng": r.lng,
            "confidence": round(float(r.confidence), 3),
            "reason": r.reason,
            "source": r.source,
            "extra": r.extra or {},
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Detectors
# ---------------------------------------------------------------------------
def discover_new_venues(db: Session, city: str, *, limit: int = 50) -> dict:
    """Use the OSM importer in preview-mode and filter out venues we already
    have (by osm_id OR name+coords)."""
    try:
        pv = osm_preview(city=city, limit=limit * 2)
    except Exception as exc:  # pragma: no cover
        logger.warning("discovery osm_preview failed for %s: %s", city, exc)
        return {"city": city, "items": _list_pending(db, city, "new"), "stale": True}

    existing_osm = {
        p.osm_id for p in db.query(VenueProfile).filter(VenueProfile.osm_id.isnot(None)).all()
    }
    existing_names = {(v.name.lower(), round(v.latitude, 3), round(v.longitude, 3)) for v in db.query(Venue).all()}

    added = 0
    for c in pv["candidates"][:limit]:
        if c["osm_id"] in existing_osm:
            continue
        key = (c["name"].lower(), round(c["lat"], 3), round(c["lng"], 3))
        if key in existing_names:
            continue
        confidence = 0.4
        if c["tags"].get("website"):
            confidence += 0.2
        if c["opening_hours_raw"]:
            confidence += 0.2
        if c["category"] == "live_music":
            confidence += 0.1
        _upsert_candidate(
            db, city=city, kind="new", name=c["name"],
            lat=c["lat"], lng=c["lng"],
            confidence=round(min(1.0, confidence), 3),
            reason=f"OSM {c['osm_type']} (amenity={c['tags'].get('amenity','?')})",
            source="osm",
            extra={"osm_id": c["osm_id"], "tags": c["tags"]},
        )
        added += 1
    return {"city": city, "added": added, "items": _list_pending(db, city, "new")}


def detect_closed_venues(db: Session, city: str, *, idle_days: int = 30) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(days=idle_days)
    venues = db.query(Venue, VenueProfile).outerjoin(
        VenueProfile, VenueProfile.venue_id == Venue.id,
    ).all()
    flagged = 0
    for venue, profile in venues:
        if profile and profile.city and city and profile.city.lower() != city.lower():
            continue
        tags = (profile.tags if profile else {}) or {}
        status_tag = tags.get("disused") or tags.get("closed") or tags.get("abandoned")

        last_history = (
            db.query(VenueVibeHistory)
            .filter(VenueVibeHistory.venue_id == venue.id)
            .order_by(VenueVibeHistory.timestamp.desc())
            .first()
        )
        no_signals = (last_history is None) or (last_history.timestamp < cutoff)

        if status_tag or no_signals:
            confidence = 0.55
            reasons = []
            if status_tag:
                confidence += 0.35
                reasons.append(f"OSM tag {status_tag}")
            if no_signals:
                confidence += 0.1
                reasons.append(f"no signals for ≥{idle_days}d")
            _upsert_candidate(
                db, city=city or (profile.city if profile else ""),
                kind="closed",
                name=venue.name, lat=venue.latitude, lng=venue.longitude,
                confidence=round(min(1.0, confidence), 3),
                reason="; ".join(reasons) or "no signals",
                source="heuristic",
                extra={"venue_id": venue.id},
            )
            flagged += 1
    return {"city": city, "flagged": flagged, "items": _list_pending(db, city, "closed")}


def detect_trending_venues(db: Session, city: str, *, limit: int = 10) -> dict:
    """Rank venues by multi-signal surge in the last 2 hours."""
    since = datetime.now(timezone.utc) - timedelta(hours=2)
    rows = []
    for v in db.query(Venue).all():
        history = (
            db.query(VenueVibeHistory)
            .filter(VenueVibeHistory.venue_id == v.id, VenueVibeHistory.timestamp >= since)
            .order_by(VenueVibeHistory.timestamp.asc())
            .all()
        )
        if len(history) < 2:
            continue
        delta = float(history[-1].vibe_score or 0.0) - float(history[0].vibe_score or 0.0)
        momentum = delta
        intel = db.get(VenueIntel, v.id)
        social = ((intel.signals or {}).get("social", {}) if intel else {}).get("ig_score", 0) or 0
        footfall = ((intel.signals or {}).get("footfall", {}) if intel else {}).get("distinct_devices_2h", 0) or 0
        score = (momentum * 0.6) + (float(social) / 100 * 0.25) + (float(footfall) / 10 * 0.15)
        if score <= 0.4:
            continue

        profile = db.get(VenueProfile, v.id)
        if city and profile and profile.city and profile.city.lower() != city.lower():
            continue

        rows.append({
            "venue": v, "momentum": momentum, "social": social, "footfall": footfall,
            "score": score,
        })
    rows.sort(key=lambda x: x["score"], reverse=True)

    items = []
    for r in rows[:limit]:
        v = r["venue"]
        reason = f"Δvibe {r['momentum']:+.2f} · social {r['social']} · visitors {r['footfall']}"
        _upsert_candidate(
            db, city=city or "", kind="trending",
            name=v.name, lat=v.latitude, lng=v.longitude,
            confidence=round(min(1.0, r["score"] / 2.0), 3),
            reason=reason, source="heuristic", extra={"venue_id": v.id},
        )
        items.append({
            "id": v.id, "name": v.name, "lat": v.latitude, "lng": v.longitude,
            "momentum": round(r["momentum"], 3),
            "score": round(r["score"], 3), "reason": reason,
        })
    return {"city": city, "count": len(items), "items": items}


# ---------------------------------------------------------------------------
# Candidate lifecycle
# ---------------------------------------------------------------------------
def approve_candidate(db: Session, candidate_id: str) -> dict:
    from app.models.venue import VenueCategory
    cand = db.get(VenueDiscoveryCandidate, candidate_id)
    if cand is None:
        raise ValueError("candidate not found")
    if cand.kind != "new":
        cand.status = "approved"
        db.commit()
        return {"approved": cand.id, "kind": cand.kind, "note": "non-new approval is flag-only"}

    # Create the live Venue + Vibe + VenueProfile
    v = Venue(
        name=cand.name,
        category=VenueCategory("bar"),
        latitude=cand.lat, longitude=cand.lng,
    )
    db.add(v)
    db.flush()
    db.add(Vibe(venue_id=v.id))
    extra = cand.extra or {}
    db.add(VenueProfile(
        venue_id=v.id, osm_id=extra.get("osm_id"), tags=extra.get("tags") or {}, city=cand.city,
    ))
    cand.status = "approved"
    db.commit()
    return {"approved": cand.id, "venue_id": v.id, "kind": cand.kind}


def reject_candidate(db: Session, candidate_id: str) -> dict:
    cand = db.get(VenueDiscoveryCandidate, candidate_id)
    if cand is None:
        raise ValueError("candidate not found")
    cand.status = "rejected"
    db.commit()
    return {"rejected": cand.id, "kind": cand.kind}
