"""Iter 16 — Re-verification flow."""
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
        v = Venue(id=str(uuid.uuid4()), name="ITER16_RV_"+uuid.uuid4().hex[:6],
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


def test_reverify_after_expiry_restores_verified_badge():
    v = _mk()
    email = f"r{uuid.uuid4().hex[:6]}@ex.com"
    _verify(v, email)
    client.post(f"/api/admin/venue/{v.id}/ownership/expire?reviewer=t")
    # Confirm expired
    intel = client.get(f"/api/intel/score/{v.id}").json()
    assert intel["is_verified"] is False
    # Kick off reverify
    rev = client.post("/api/claims/reverify", json={
        "venue_id": v.id, "email": email, "owner_name": "O", "proof": "still me",
    }).json()
    assert rev["reverify"] is True
    assert rev["status"] == "email_sent"
    tok = rev["magic_link"].rsplit("/", 1)[-1]
    done = client.get(f"/api/claims/verify/{tok}").json()
    assert done["ok"] is True
    # Now verified again
    intel2 = client.get(f"/api/intel/score/{v.id}").json()
    assert intel2["is_verified"] is True


def test_reverify_payload_validation():
    # unknown venue
    r = client.post("/api/claims/reverify", json={"venue_id": "nope", "email": "x@ex.com"})
    assert r.status_code == 404
