"""Iter 16 — First verified visit reward loop."""
from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models import Venue, VenueCategory, Vibe

client = TestClient(app)


def _mk(verified=False):
    db = SessionLocal()
    try:
        v = Venue(id=str(uuid.uuid4()), name="ITER16_FV_"+uuid.uuid4().hex[:6],
                  category=VenueCategory.bar, latitude=40.73, longitude=-73.99)
        db.add(v); db.flush(); db.add(Vibe(venue_id=v.id)); db.commit(); db.refresh(v)
    finally: db.close()
    if verified:
        email = f"fv{uuid.uuid4().hex[:6]}@ex.com"
        sub = client.post("/api/claims/submit", json={
            "venue_id": v.id, "owner_name": "O", "email": email, "proof": "",
        }).json()
        tok = sub["magic_link"].rsplit("/", 1)[-1]
        client.get(f"/api/claims/verify/{tok}")
    return v


def test_reward_awarded_to_first_visitor_on_verified_venue():
    v = _mk(verified=True)
    dev = "dev_" + uuid.uuid4().hex[:10]
    r = client.post("/api/intel/visits/check-in", json={"venue_id": v.id, "device_id": dev}).json()
    assert r["awarded"] is True
    assert r["bonus_credits"] == 15
    assert r["balance"] >= 15


def test_second_visitor_same_day_not_rewarded():
    v = _mk(verified=True)
    d1 = "dev_" + uuid.uuid4().hex[:10]
    d2 = "dev_" + uuid.uuid4().hex[:10]
    client.post("/api/intel/visits/check-in", json={"venue_id": v.id, "device_id": d1})
    r = client.post("/api/intel/visits/check-in", json={"venue_id": v.id, "device_id": d2}).json()
    assert r["awarded"] is False
    assert r["reason"] == "not_first_visitor"


def test_same_user_retry_idempotent():
    v = _mk(verified=True)
    d = "dev_" + uuid.uuid4().hex[:10]
    first = client.post("/api/intel/visits/check-in", json={"venue_id": v.id, "device_id": d}).json()
    assert first["awarded"] is True
    again = client.post("/api/intel/visits/check-in", json={"venue_id": v.id, "device_id": d}).json()
    assert again["awarded"] is False
    assert again["reason"] == "already_rewarded_today"


def test_unverified_venue_does_not_reward():
    v = _mk(verified=False)
    d = "dev_" + uuid.uuid4().hex[:10]
    r = client.post("/api/intel/visits/check-in", json={"venue_id": v.id, "device_id": d}).json()
    assert r["awarded"] is False
    assert r["reason"] == "venue_not_verified"


def test_admin_first_visit_history_lists_reward_day_marker():
    v = _mk(verified=True)
    d = "dev_" + uuid.uuid4().hex[:10]
    client.post("/api/intel/visits/check-in", json={"venue_id": v.id, "device_id": d})
    items = client.get("/api/admin/rewards/first-visits").json()["items"]
    assert any(it["venue_id"] == v.id and it["kind"] == "FIRST_VERIFIED_VISIT" for it in items)


def test_owner_webhook_fires_on_first_verified_visit(monkeypatch):
    """With a valid owner slack URL (httpbin bypassing prefix via raw meta),
    a first-visit reward triggers OWNER:FIRST_VERIFIED_VISIT in the log."""
    v = _mk(verified=True)
    # Find the verified claim and write a test URL directly to meta.webhooks
    from app.core.database import SessionLocal as S
    from app.models import VenueClaim
    s = S()
    try:
        c = s.query(VenueClaim).filter(
            VenueClaim.venue_id == v.id, VenueClaim.status == "verified",
        ).first()
        c.meta = {**(c.meta or {}),
                  "webhooks": {"slack_webhook_url": "https://httpbin.org/post"}}
        s.commit()
    finally: s.close()

    d = "dev_" + uuid.uuid4().hex[:10]
    r = client.post("/api/intel/visits/check-in", json={"venue_id": v.id, "device_id": d}).json()
    assert r["awarded"] is True
    import time; time.sleep(6)
    events = client.get("/api/admin/webhooks/recent?limit=50").json()["recent"]
    assert any(
        e["event_type"] == "OWNER:FIRST_VERIFIED_VISIT"
        and e.get("meta", {}).get("venue_id") == v.id
        for e in events
    ), [e["event_type"] for e in events[:5]]
