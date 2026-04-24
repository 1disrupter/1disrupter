"""Iter 16 — Ownership expiry (admin)."""
from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models import Venue, VenueCategory, Vibe

client = TestClient(app)


def _mk():
    db = SessionLocal()
    try:
        v = Venue(id=str(uuid.uuid4()), name="ITER16_EXP_"+uuid.uuid4().hex[:6],
                  category=VenueCategory.bar, latitude=40.73, longitude=-73.99)
        db.add(v); db.flush(); db.add(Vibe(venue_id=v.id)); db.commit(); db.refresh(v)
        return v
    finally: db.close()


def _verify(v, email):
    sub = client.post("/api/claims/submit", json={
        "venue_id": v.id, "owner_name": "O", "email": email, "proof": "",
    }).json()
    tok = sub["magic_link"].rsplit("/", 1)[-1]
    return client.get(f"/api/claims/verify/{tok}").json()["owner_api_key"]


def test_expire_endpoint_marks_claim_needs_reverify_and_invalidates_key():
    v = _mk()
    key = _verify(v, f"a{uuid.uuid4().hex[:6]}@ex.com")
    r = client.post(f"/api/admin/venue/{v.id}/ownership/expire?reviewer=tester")
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert r.json()["affected"] >= 1
    # Key is invalidated
    assert client.get("/api/owner/me", headers={"X-Owner-Key": key}).status_code == 401


def test_expire_removes_verified_badge_from_public_api():
    v = _mk()
    _verify(v, f"a{uuid.uuid4().hex[:6]}@ex.com")
    # Present in verified list
    rows = client.get("/api/admin/venues?verified_only=true").json()["items"]
    assert any(x["venue"]["id"] == v.id for x in rows)
    # Expire
    client.post(f"/api/admin/venue/{v.id}/ownership/expire?reviewer=tester")
    # Gone from verified list
    rows2 = client.get("/api/admin/venues?verified_only=true").json()["items"]
    assert all(x["venue"]["id"] != v.id for x in rows2)
    # And is_verified=False on intel score
    intel = client.get(f"/api/intel/score/{v.id}").json()
    assert intel["is_verified"] is False


def test_expire_on_unclaimed_venue_returns_400():
    v = _mk()
    r = client.post(f"/api/admin/venue/{v.id}/ownership/expire")
    assert r.status_code == 400


def test_claim_status_moves_to_needs_reverify():
    v = _mk()
    email = f"a{uuid.uuid4().hex[:6]}@ex.com"
    _verify(v, email)
    client.post(f"/api/admin/venue/{v.id}/ownership/expire?reviewer=t")
    # Admin claims listing shows the row with needs_reverify
    items = client.get("/api/admin/claims").json()["items"]
    hit = [c for c in items if c["venue_id"] == v.id and c["email"] == email]
    assert hit and hit[0]["status"] == "needs_reverify"
