"""Iter 16 — Ownership transfer (request + accept)."""
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
        v = Venue(id=str(uuid.uuid4()), name="ITER16_TR_"+uuid.uuid4().hex[:6],
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


def test_transfer_request_marks_meta_and_returns_magic_link():
    v = _mk()
    email_a = f"a{uuid.uuid4().hex[:6]}@ex.com"
    email_b = f"b{uuid.uuid4().hex[:6]}@ex.com"
    key = _verify(v, email_a)
    r = client.post(f"/api/owner/venue/{v.id}/transfer/request",
                    headers={"X-Owner-Key": key}, json={"email": email_b})
    assert r.status_code == 200
    body = r.json()
    assert body["transfer_requested"] is True
    assert body["transfer_email"] == email_b
    assert body["magic_link"] and "/api/owner/transfer/accept/" in body["magic_link"]


def test_transfer_accept_rotates_api_key_and_owner():
    v = _mk()
    email_a = f"a{uuid.uuid4().hex[:6]}@ex.com"
    email_b = f"b{uuid.uuid4().hex[:6]}@ex.com"
    key_a = _verify(v, email_a)
    req = client.post(f"/api/owner/venue/{v.id}/transfer/request",
                      headers={"X-Owner-Key": key_a}, json={"email": email_b}).json()
    tok = req["magic_link"].rsplit("/", 1)[-1]
    acc = client.get(f"/api/owner/transfer/accept/{tok}").json()
    assert acc["ok"] is True
    assert acc["new_owner_email"] == email_b
    new_key = acc["owner_api_key"]
    assert new_key and new_key != key_a

    # Old key must 401 now
    assert client.get("/api/owner/me", headers={"X-Owner-Key": key_a}).status_code == 401
    # New key must succeed and own the venue
    me = client.get("/api/owner/me", headers={"X-Owner-Key": new_key}).json()
    assert any(vn["id"] == v.id for vn in me["venues"])


def test_transfer_token_is_single_use():
    v = _mk()
    key = _verify(v, f"a{uuid.uuid4().hex[:6]}@ex.com")
    req = client.post(f"/api/owner/venue/{v.id}/transfer/request",
                      headers={"X-Owner-Key": key},
                      json={"email": f"b{uuid.uuid4().hex[:6]}@ex.com"}).json()
    tok = req["magic_link"].rsplit("/", 1)[-1]
    client.get(f"/api/owner/transfer/accept/{tok}")
    r2 = client.get(f"/api/owner/transfer/accept/{tok}")
    assert r2.status_code == 400


def test_transfer_request_requires_ownership():
    v = _mk()
    key = _verify(v, f"a{uuid.uuid4().hex[:6]}@ex.com")
    other = _mk()
    r = client.post(f"/api/owner/venue/{other.id}/transfer/request",
                    headers={"X-Owner-Key": key}, json={"email": "z@ex.com"})
    assert r.status_code == 403
