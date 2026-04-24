# -*- coding: utf-8 -*-
"""OpenStreetMap importer — Overpass API, no key required.

- `preview(city=..., bbox=...)` → list of candidates without writing anything.
- `import_osm(...)` → upserts Venue + VenueProfile rows (dedupe on osm_id OR
  case-insensitive name + ~50m proximity). Existing metadata never overwritten
  unless `overwrite=True`.
"""
from __future__ import annotations

import logging
import math
from typing import Any, Iterable, Optional

import requests
from sqlalchemy.orm import Session

from app.models import Venue, Vibe
from app.models.launch import VenueProfile
from app.models.venue import VenueCategory

logger = logging.getLogger("vibe2nite.osm")

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

# OSM amenity tags → our category enum
AMENITY_MAP: dict[str, str] = {
    "bar": "bar",
    "pub": "bar",
    "biergarten": "bar",
    "nightclub": "club",
    "restaurant": "bar",       # default — narrow later
    "music_venue": "live_music",
}

HEADERS = {
    "User-Agent": "Vibe2Nite/1.0 (https://vibe2nite.app; contact@vibe2nite.app)",
}


def _geocode_bbox(city: str) -> Optional[tuple[float, float, float, float]]:
    """Return (lat_min, lat_max, lon_min, lon_max) for `city` via Nominatim."""
    try:
        r = requests.get(
            NOMINATIM_URL,
            params={"q": city, "format": "json", "limit": 1},
            headers=HEADERS,
            timeout=8,
        )
        r.raise_for_status()
        items = r.json() or []
        if not items:
            return None
        bb = items[0].get("boundingbox")
        if not bb or len(bb) != 4:
            return None
        # Nominatim: [lat_min, lat_max, lon_min, lon_max] as strings
        return (float(bb[0]), float(bb[1]), float(bb[2]), float(bb[3]))
    except Exception as exc:  # pragma: no cover
        logger.warning("geocode failed for %s: %s", city, exc)
        return None


def _overpass_query(bbox: tuple[float, float, float, float]) -> str:
    lat_min, lat_max, lon_min, lon_max = bbox
    south, west, north, east = lat_min, lon_min, lat_max, lon_max
    # Node + way + relation; nightlife + eating
    return f"""
    [out:json][timeout:25];
    (
      node["amenity"~"bar|pub|biergarten|nightclub|restaurant|music_venue"]({south},{west},{north},{east});
      way["amenity"~"bar|pub|biergarten|nightclub|restaurant|music_venue"]({south},{west},{north},{east});
      node["leisure"="adult_gaming_centre"]({south},{west},{north},{east});
    );
    out center tags;
    """


def _fetch_overpass(query: str) -> list[dict]:
    last_err: Optional[Exception] = None
    for url in OVERPASS_URLS:
        try:
            r = requests.post(url, data={"data": query}, headers=HEADERS, timeout=30)
            r.raise_for_status()
            return r.json().get("elements", [])
        except Exception as exc:  # pragma: no cover
            last_err = exc
            logger.warning("overpass failed at %s: %s", url, exc)
    if last_err:
        raise last_err
    return []


def _extract_candidate(el: dict) -> Optional[dict]:
    tags = el.get("tags") or {}
    name = (tags.get("name") or "").strip()
    if not name:
        return None
    amenity = tags.get("amenity") or ""
    if amenity not in AMENITY_MAP and "music" not in tags.get("music", "").lower():
        # For restaurants w/o bar context, skip unless they are music venues
        if amenity != "restaurant" or not tags.get("live_music"):
            return None
    # Node has lat/lon; way/relation have "center"
    if "lat" in el and "lon" in el:
        lat, lon = el["lat"], el["lon"]
    elif el.get("center"):
        lat, lon = el["center"]["lat"], el["center"]["lon"]
    else:
        return None

    category = AMENITY_MAP.get(amenity, "bar")
    if tags.get("live_music") in ("yes", "true") or amenity == "music_venue":
        category = "live_music"

    return {
        "osm_id": f"{el.get('type', 'node')}/{el.get('id')}",
        "osm_type": el.get("type", "node"),
        "name": name,
        "lat": float(lat),
        "lng": float(lon),
        "category": category,
        "opening_hours_raw": tags.get("opening_hours", "") or "",
        "tags": {
            k: v for k, v in tags.items()
            if k in {
                "amenity", "cuisine", "music", "live_music",
                "smoking", "outdoor_seating", "wheelchair", "website",
                "phone", "brand", "dress_code",
            }
        },
    }


def _haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _parse_opening_hours(raw: str) -> dict[str, str]:
    """Very forgiving OSM `opening_hours` parser — best-effort for admin preview.
    Returns `{}` if unparseable."""
    if not raw:
        return {}
    mapping = {
        "Mo": "mon", "Tu": "tue", "We": "wed", "Th": "thu",
        "Fr": "fri", "Sa": "sat", "Su": "sun",
    }
    out: dict[str, str] = {}
    # Split on ";" — e.g. "Mo-Th 18:00-02:00; Fr-Sa 18:00-04:00"
    for block in (b.strip() for b in raw.split(";")):
        if not block or " " not in block:
            continue
        day_spec, hours = block.split(" ", 1)
        days: list[str] = []
        for chunk in day_spec.split(","):
            if "-" in chunk and len(chunk) == 5:
                a, b = chunk.split("-")
                if a in mapping and b in mapping:
                    order = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
                    i1, i2 = order.index(a), order.index(b)
                    days.extend(order[i1:i2 + 1])
            elif chunk in mapping:
                days.append(chunk)
        for d in days:
            out[mapping[d]] = hours.strip()
    return out


def preview(
    *, city: Optional[str] = None,
    bbox: Optional[tuple[float, float, float, float]] = None,
    limit: int = 200,
) -> dict:
    if bbox is None:
        if not city:
            raise ValueError("city or bbox required")
        bbox = _geocode_bbox(city)
        if bbox is None:
            raise ValueError(f"could not geocode city: {city!r}")
    els = _fetch_overpass(_overpass_query(bbox))
    cands: list[dict] = []
    for el in els:
        c = _extract_candidate(el)
        if c is not None:
            cands.append(c)
        if len(cands) >= limit:
            break
    return {
        "city": city,
        "bbox": list(bbox),
        "total_elements": len(els),
        "candidates": cands,
        "count": len(cands),
    }


def import_osm(
    db: Session, *,
    city: Optional[str] = None,
    bbox: Optional[tuple[float, float, float, float]] = None,
    overwrite: bool = False,
    limit: int = 500,
    candidates: Optional[list[dict]] = None,
) -> dict:
    """Ingest OSM candidates as Venue + VenueProfile rows.
    Passing `candidates` skips the network fetch (used by preview-then-confirm flow)."""
    if candidates is None:
        pv = preview(city=city, bbox=bbox, limit=limit)
        candidates = pv["candidates"]

    imported = 0
    skipped = 0
    updated = 0

    for c in candidates:
        try:
            existing: Optional[Venue] = None

            # Match by osm_id first.
            profile_osm = (
                db.query(VenueProfile)
                .filter(VenueProfile.osm_id == c["osm_id"])
                .one_or_none()
            )
            if profile_osm is not None:
                existing = db.get(Venue, profile_osm.venue_id)

            if existing is None:
                # Fallback: name (case-insensitive) + <50m proximity.
                candidates_name = (
                    db.query(Venue)
                    .filter(Venue.name.ilike(c["name"]))
                    .all()
                )
                for v in candidates_name:
                    if _haversine_m(v.latitude, v.longitude, c["lat"], c["lng"]) < 50.0:
                        existing = v
                        break

            if existing is None:
                v = Venue(
                    name=c["name"],
                    category=VenueCategory(c["category"]),
                    latitude=c["lat"],
                    longitude=c["lng"],
                )
                db.add(v)
                db.flush()
                db.add(Vibe(venue_id=v.id))
                profile = VenueProfile(
                    venue_id=v.id,
                    osm_id=c["osm_id"],
                    osm_type=c["osm_type"],
                    tags=c["tags"],
                    opening_hours=_parse_opening_hours(c["opening_hours_raw"]),
                    city=city or "",
                )
                db.add(profile)
                imported += 1
            else:
                profile = db.get(VenueProfile, existing.id)
                if profile is None:
                    profile = VenueProfile(venue_id=existing.id)
                    db.add(profile)
                    db.flush()
                if overwrite:
                    profile.osm_id = c["osm_id"]
                    profile.osm_type = c["osm_type"]
                    profile.tags = c["tags"]
                    if c["opening_hours_raw"]:
                        profile.opening_hours = _parse_opening_hours(c["opening_hours_raw"])
                    if city:
                        profile.city = city
                    updated += 1
                else:
                    # Only fill empties — never clobber admin-entered data.
                    if not profile.osm_id:
                        profile.osm_id = c["osm_id"]
                        profile.osm_type = c["osm_type"]
                    if not profile.tags:
                        profile.tags = c["tags"]
                    if not profile.opening_hours and c["opening_hours_raw"]:
                        profile.opening_hours = _parse_opening_hours(c["opening_hours_raw"])
                    if not profile.city and city:
                        profile.city = city
                    updated += 1 if (profile.osm_id == c["osm_id"]) else 0
                    skipped += 1 if updated == 0 else 0
            db.commit()
        except Exception as exc:  # pragma: no cover
            db.rollback()
            logger.exception("osm import failed for %s: %s", c.get("name"), exc)
            skipped += 1
    return {
        "city": city,
        "imported_count": imported,
        "updated_count": updated,
        "skipped_count": skipped,
        "total_candidates": len(candidates),
    }
