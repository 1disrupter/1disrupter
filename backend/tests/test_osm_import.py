# -*- coding: utf-8 -*-
"""OpenStreetMap importer tests."""
from __future__ import annotations

import os
from unittest.mock import patch

import pytest
import requests

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def test_osm_import_requires_city_or_bbox(session):
    r = session.post(f"{API}/import/osm", json={})
    assert r.status_code == 400


def test_osm_dry_run_bbox(session):
    body = {
        "bbox": {"lat_min": 36.58, "lat_max": 36.62, "lon_min": -4.54, "lon_max": -4.49},
        "dry_run": True, "limit": 5,
    }
    r = session.post(f"{API}/import/osm", json=body, timeout=30)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "candidates" in data
    assert data["count"] <= 5
    if data["candidates"]:
        first = data["candidates"][0]
        assert {"name", "lat", "lng", "category", "osm_id"} <= set(first)


def test_osm_real_import_bbox_dedupes(session):
    body = {
        "bbox": {"lat_min": 36.58, "lat_max": 36.62, "lon_min": -4.54, "lon_max": -4.49},
        "limit": 5,
    }
    r1 = session.post(f"{API}/import/osm", json=body, timeout=60)
    assert r1.status_code == 200
    first_imported = r1.json()["imported_count"]
    # Second run should import zero new rows (dedupe by osm_id).
    r2 = session.post(f"{API}/import/osm", json=body, timeout=60)
    assert r2.json()["imported_count"] == 0
    assert (r2.json()["updated_count"] + r2.json()["skipped_count"]) > 0


def test_osm_parse_helpers():
    """Import parse helpers work without hitting the network."""
    from app.services.osm_import import _parse_opening_hours, _extract_candidate
    hours = _parse_opening_hours("Mo-Th 18:00-02:00; Fr-Sa 18:00-04:00")
    assert hours["mon"] == "18:00-02:00"
    assert hours["sat"] == "18:00-04:00"

    el = {
        "type": "node", "id": 42, "lat": 40.758, "lon": -73.985,
        "tags": {"name": "Copper Canary", "amenity": "bar", "opening_hours": "Mo 20:00-02:00"},
    }
    c = _extract_candidate(el)
    assert c and c["name"] == "Copper Canary"
    assert c["category"] == "bar"
    assert c["osm_id"] == "node/42"


def test_osm_skips_unnamed_elements():
    from app.services.osm_import import _extract_candidate
    assert _extract_candidate({"type": "node", "id": 1, "lat": 0, "lon": 0, "tags": {"amenity": "bar"}}) is None
