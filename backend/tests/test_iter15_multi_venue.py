"""Iter 15 — Multi-venue ownership."""
from __future__ import annotations

import uuid
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models import Venue, VenueCategory, Vibe

client = TestClient(app)


def _mk_venue(name):
    db = SessionLocal()
    try:
        v = Venue(id=str(uuid.uuid4()), name=name, category=VenueCategory.bar,
                  latitude=40.73, longitude=-73.99)
        db.add(v); db.flush()
        db.add(Vibe(venue_id=v.id))
        db.commit(); db.refresh(v)
        return v
    finally:
        db.close()


def _verify(venue, email):
    sub = client.post("/api/claims/submit", json={
        "venue_id": venue.id, "owner_name": "Multi", "email": email, "proof": ""
    }).json()
    t = sub["magic_link"].rsplit("/", 1)[-1]
    return client.get(f"/api/claims/verify/{t}").json()["owner_api_key"]


def test_single_venue_owner_returns_one_item():
    v = _mk_venue("ITER15_SV")
    key = _verify(v, f"sv{uuid.uuid4().hex[:6]}@ex.com")
    r = client.get("/api/owner/venues", headers={"X-Owner-Key": key})
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 1
    assert body["items"][0]["id"] == v.id
    assert body["items"][0]["is_verified"] is True


def test_multi_venue_owner_returns_all_verified_venues():
    email = f"mv{uuid.uuid4().hex[:6]}@ex.com"
    v1 = _mk_venue("ITER15_MV1")
    v2 = _mk_venue("ITER15_MV2")
    v3 = _mk_venue("ITER15_MV3")
    keys = [_verify(v1, email), _verify(v2, email), _verify(v3, email)]
    # Any of the keys must resolve to all three owned venues
    for k in keys:
        r = client.get("/api/owner/venues", headers={"X-Owner-Key": k})
        assert r.status_code == 200
        ids = {x["id"] for x in r.json()["items"]}
        assert {v1.id, v2.id, v3.id} <= ids


def test_me_reports_venue_count_for_multi_owner():
    email = f"mv2{uuid.uuid4().hex[:6]}@ex.com"
    a = _mk_venue("ITER15_MV_A")
    b = _mk_venue("ITER15_MV_B")
    key = _verify(a, email)
    _verify(b, email)
    me = client.get("/api/owner/me", headers={"X-Owner-Key": key}).json()
    assert me["owner"]["venue_count"] >= 2


def test_set_handles_for_other_owned_venue_succeeds():
    email = f"mv3{uuid.uuid4().hex[:6]}@ex.com"
    a = _mk_venue("ITER15_MVH_A")
    b = _mk_venue("ITER15_MVH_B")
    key = _verify(a, email)
    _verify(b, email)
    r = client.put(f"/api/owner/venue/{b.id}/handles",
                   headers={"X-Owner-Key": key},
                   json={"instagram": "@venueb"})
    assert r.status_code == 200
    assert r.json()["social_handles"]["instagram"] == "venueb"


def test_set_handles_for_unowned_venue_is_forbidden():
    email = f"mv4{uuid.uuid4().hex[:6]}@ex.com"
    a = _mk_venue("ITER15_U_A")
    unowned = _mk_venue("ITER15_UNOWNED")
    key = _verify(a, email)
    r = client.put(f"/api/owner/venue/{unowned.id}/handles",
                   headers={"X-Owner-Key": key},
                   json={"instagram": "@evil"})
    assert r.status_code == 403
