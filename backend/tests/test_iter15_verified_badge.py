"""Iter 15 — Verified ✓ badge exposure in API responses."""
from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models import Venue, VenueCategory, Vibe

client = TestClient(app)


def _mk_venue(name="ITER15_VERIFIED", lat=40.73, lng=-73.99):
    db = SessionLocal()
    try:
        v = Venue(id=str(uuid.uuid4()), name=name, category=VenueCategory.bar,
                  latitude=lat, longitude=lng)
        db.add(v)
        db.flush()
        db.add(Vibe(venue_id=v.id))
        db.commit()
        db.refresh(v)
        return v
    finally:
        db.close()


def _verify(v: Venue) -> str:
    sub = client.post("/api/claims/submit", json={
        "venue_id": v.id, "owner_name": "V", "email": f"v{uuid.uuid4().hex[:6]}@ex.com", "proof": ""
    }).json()
    t = sub["magic_link"].rsplit("/", 1)[-1]
    return client.get(f"/api/claims/verify/{t}").json()["owner_api_key"]


def test_top_feed_includes_is_verified_field_on_unverified_venue():
    v = _mk_venue(name="ITER15_TOP", lat=40.73, lng=-73.99)
    r = client.get("/api/vibes/top?lat=40.73&lng=-73.99&radius_km=1")
    assert r.status_code == 200
    # best_overall must have the field (defaulting to False when no claim)
    best = r.json()["best_overall"]
    assert best is not None
    assert "is_verified" in best["venue"]


def test_admin_venues_marks_verified_after_claim_approved():
    v = _mk_venue(name="ITER15_ADMIN")
    _verify(v)
    rows = client.get("/api/admin/venues").json()["items"]
    hit = [x for x in rows if x["venue"]["id"] == v.id]
    assert hit and hit[0]["venue"]["is_verified"] is True


def test_admin_venues_verified_only_filter():
    total = client.get("/api/admin/venues").json()["count"]
    filtered = client.get("/api/admin/venues?verified_only=true").json()["count"]
    assert filtered <= total
    # every row we get back must be verified
    rows = client.get("/api/admin/venues?verified_only=true").json()["items"]
    assert all(r["venue"]["is_verified"] for r in rows)


def test_venues_list_includes_is_verified_and_filter():
    v = _mk_venue(name="ITER15_LIST")
    _verify(v)
    rows = client.get("/api/venues/list").json()["items"]
    hit = [x for x in rows if x["id"] == v.id]
    assert hit and hit[0]["is_verified"] is True

    only = client.get("/api/venues/list?verified_only=true").json()
    assert all(x["is_verified"] for x in only["items"])


def test_intel_score_includes_is_verified():
    v = _mk_venue(name="ITER15_INTEL")
    r = client.get(f"/api/intel/score/{v.id}").json()
    assert r["is_verified"] is False
    _verify(v)
    r2 = client.get(f"/api/intel/score/{v.id}").json()
    assert r2["is_verified"] is True
