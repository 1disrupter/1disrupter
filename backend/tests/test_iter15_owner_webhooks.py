"""Iter 15 — Owner-triggered webhook subscriptions."""
from __future__ import annotations

import uuid
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models import Venue, VenueCategory, Vibe

client = TestClient(app)


def _mk_and_verify(name="ITER15_HOOK"):
    db = SessionLocal()
    try:
        v = Venue(id=str(uuid.uuid4()), name=name, category=VenueCategory.bar,
                  latitude=40.73, longitude=-73.99)
        db.add(v); db.flush()
        db.add(Vibe(venue_id=v.id))
        db.commit(); db.refresh(v)
    finally:
        db.close()
    sub = client.post("/api/claims/submit", json={
        "venue_id": v.id, "owner_name": "H", "email": f"h{uuid.uuid4().hex[:6]}@ex.com", "proof": "",
    }).json()
    t = sub["magic_link"].rsplit("/", 1)[-1]
    key = client.get(f"/api/claims/verify/{t}").json()["owner_api_key"]
    return v, key


def test_invalid_slack_url_rejected():
    v, key = _mk_and_verify()
    r = client.put(
        f"/api/owner/venue/{v.id}/webhooks",
        headers={"X-Owner-Key": key},
        json={"slack_webhook_url": "http://example.com/evil"},
    )
    assert r.status_code == 400
    assert "hooks.slack.com" in r.json()["detail"]


def test_invalid_discord_url_rejected():
    v, key = _mk_and_verify()
    r = client.put(
        f"/api/owner/venue/{v.id}/webhooks",
        headers={"X-Owner-Key": key},
        json={"discord_webhook_url": "https://not-discord.com/x"},
    )
    assert r.status_code == 400


def test_valid_urls_accepted_and_persisted():
    v, key = _mk_and_verify()
    r = client.put(
        f"/api/owner/venue/{v.id}/webhooks",
        headers={"X-Owner-Key": key},
        json={
            "slack_webhook_url":   "https://hooks.slack.com/services/T/B/X",
            "discord_webhook_url": "https://discord.com/api/webhooks/1/abc",
        },
    )
    assert r.status_code == 200
    me = client.get("/api/owner/me", headers={"X-Owner-Key": key}).json()
    vv = [x for x in me["venues"] if x["id"] == v.id][0]
    assert vv["webhooks"]["slack_webhook_url"].startswith("https://hooks.slack.com/")
    assert vv["webhooks"]["discord_webhook_url"].startswith("https://discord.com/api/webhooks/")


def test_empty_urls_clear_webhooks():
    v, key = _mk_and_verify()
    client.put(f"/api/owner/venue/{v.id}/webhooks", headers={"X-Owner-Key": key},
               json={"slack_webhook_url": "https://hooks.slack.com/services/T/B/X"})
    r = client.put(f"/api/owner/venue/{v.id}/webhooks", headers={"X-Owner-Key": key},
                   json={"slack_webhook_url": ""})
    assert r.status_code == 200
    assert r.json()["webhooks"]["slack_webhook_url"] == ""


def test_test_webhook_requires_configured_url():
    v, key = _mk_and_verify()
    r = client.post(f"/api/owner/venue/{v.id}/webhooks/test", headers={"X-Owner-Key": key})
    assert r.status_code == 400


def test_test_webhook_fires_and_records_in_db_log():
    """Point both slack and discord URLs at httpbin.org/post (still passes the
    prefix check because we prepend hooks.slack.com/… via the httpbin mock).
    Since our validator enforces real prefixes we instead use the httpbin alias
    by bypassing the editor and writing directly to the claim meta, then fire."""
    v, key = _mk_and_verify()
    # Write URLs directly through the dispatcher's internals: use real
    # prefix but route to httpbin via the global dispatcher by config.
    from app.core.database import SessionLocal
    from app.services import owner as owner_svc
    from app.models import VenueClaim
    s = SessionLocal()
    try:
        claim = (
            s.query(VenueClaim)
            .filter(VenueClaim.venue_id == v.id, VenueClaim.status == "verified")
            .first()
        )
        meta = dict(claim.meta or {})
        # Store a test-only URL that WILL pass validation AND actually reach
        # httpbin via DNS rewriting… instead, we just point to httpbin directly
        # and bypass validation by writing raw meta.
        meta["webhooks"] = {
            "slack_webhook_url": "https://httpbin.org/post",
            "discord_webhook_url": "https://httpbin.org/post",
        }
        claim.meta = meta
        s.commit()
    finally:
        s.close()

    r = client.post(f"/api/owner/venue/{v.id}/webhooks/test", headers={"X-Owner-Key": key})
    assert r.status_code == 200
    assert r.json()["sent"] is True
    assert len(r.json()["targets"]) == 2

    import time; time.sleep(6)
    events = client.get("/api/admin/webhooks/recent?limit=20").json()["recent"]
    owner_evts = [e for e in events if e["event_type"].startswith("OWNER:")]
    assert owner_evts, "expected owner webhook event in DB-backed log"
    assert any(e["ok"] for e in owner_evts)


def test_vibe_spike_dispatch_fans_out_to_owner_webhooks(monkeypatch):
    v, key = _mk_and_verify()
    # Write httpbin URLs directly to the claim (bypass URL validator).
    from app.core.database import SessionLocal
    from app.models import VenueClaim
    s = SessionLocal()
    try:
        c = (
            s.query(VenueClaim)
            .filter(VenueClaim.venue_id == v.id, VenueClaim.status == "verified")
            .first()
        )
        c.meta = {**(c.meta or {}), "webhooks": {"slack_webhook_url": "https://httpbin.org/post"}}
        s.commit()
    finally:
        s.close()

    # Fire a VIBE_SPIKE with venue_id in meta — the global dispatcher should
    # fan out to the owner webhooks even though global URL is unset.
    from app.services import webhooks as wh
    wh.dispatch("VIBE_SPIKE", title="spike-test", body="b", meta={"venue_id": v.id})
    import time; time.sleep(6)

    events = client.get("/api/admin/webhooks/recent?limit=30").json()["recent"]
    matching = [e for e in events
                if e["event_type"] == "OWNER:VIBE_SPIKE"
                and e["meta"].get("venue_id") == v.id
                and "spike-test" in e["title"]]
    assert matching, f"expected owner fan-out for VIBE_SPIKE, got {events[:3]}"


def test_test_webhook_forbidden_for_unowned_venue():
    v1, key = _mk_and_verify()
    v2, _  = _mk_and_verify()  # different owner
    r = client.post(f"/api/owner/venue/{v2.id}/webhooks/test", headers={"X-Owner-Key": key})
    assert r.status_code == 403
