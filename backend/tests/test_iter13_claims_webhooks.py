"""Tests for Iteration 13 — claims, providers, webhooks."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models import Venue, VenueCategory, VenueClaim


client = TestClient(app)


def _mk_venue() -> Venue:
    db = SessionLocal()
    try:
        v = Venue(
            id=str(uuid.uuid4()),
            name="TEST_Iter13_Venue",
            category=VenueCategory.bar,
            latitude=40.73,
            longitude=-73.99,
        )
        db.add(v)
        db.commit()
        db.refresh(v)
        return v
    finally:
        db.close()


def test_provider_status_lists_all_providers():
    r = client.get("/api/admin/providers/status")
    assert r.status_code == 200
    providers = r.json()["providers"]
    names = {p["provider"] for p in providers}
    assert {"instagram", "tiktok", "ticketmaster", "eventbrite", "google_places"} <= names
    # With no keys configured, all are in stub mode
    assert all(p["mode"] == "stub" for p in providers)


def test_webhook_status_no_urls_configured():
    r = client.get("/api/admin/webhooks/recent")
    assert r.status_code == 200
    d = r.json()
    assert set(d["configured"].keys()) >= {"VIBE_SPIKE", "VENUE_CLAIMED", "VENUE_CLOSED"}
    assert all(v is False for v in d["configured"].values())
    assert isinstance(d["recent"], list)


def test_claim_submit_and_verify_happy_path():
    v = _mk_venue()
    r = client.post(
        "/api/claims/submit",
        json={
            "venue_id": v.id,
            "owner_name": "Alice",
            "email": "alice@example.com",
            "proof": "https://instagram.com/alice",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "email_sent"
    assert body["email_provider_live"] is False      # no RESEND_API_KEY
    assert body["magic_link"] and "/api/claims/verify/" in body["magic_link"]

    token = body["magic_link"].rsplit("/", 1)[-1]

    # Verify the token
    r2 = client.get(f"/api/claims/verify/{token}")
    assert r2.status_code == 200, r2.text
    v2 = r2.json()
    assert v2["ok"] is True
    assert v2["claim"]["status"] == "verified"

    # Token is single-use
    r3 = client.get(f"/api/claims/verify/{token}")
    assert r3.status_code == 400  # already_verified returns invalid


def test_claim_submit_unknown_venue_404():
    r = client.post(
        "/api/claims/submit",
        json={
            "venue_id": "does-not-exist",
            "owner_name": "Bob",
            "email": "bob@example.com",
            "proof": "",
        },
    )
    assert r.status_code == 404


def test_verify_invalid_token_returns_400():
    r = client.get("/api/claims/verify/not-a-real-token")
    assert r.status_code == 400


def test_verify_expired_token_returns_410():
    v = _mk_venue()
    db = SessionLocal()
    try:
        c = VenueClaim(
            id=str(uuid.uuid4()),
            venue_id=v.id,
            owner_name="Carol",
            email="carol@example.com",
            proof="",
            status="email_sent",
            token="expired-token-123",
            token_expires_at=datetime.now(timezone.utc) - timedelta(minutes=10),
        )
        db.add(c)
        db.commit()
    finally:
        db.close()

    r = client.get("/api/claims/verify/expired-token-123")
    assert r.status_code == 410


def test_admin_list_and_review_flow():
    v = _mk_venue()
    # Create a pending claim
    sub = client.post(
        "/api/claims/submit",
        json={
            "venue_id": v.id,
            "owner_name": "Dan",
            "email": "dan@example.com",
            "proof": "https://example.com",
        },
    ).json()
    claim_id = sub["claim_id"]

    # Admin list
    rows = client.get("/api/admin/claims").json()["items"]
    assert any(c["id"] == claim_id for c in rows)

    # Admin approves
    rev = client.post(f"/api/admin/claims/{claim_id}/review", json={"action": "approve", "reviewer": "tester"})
    assert rev.status_code == 200
    assert rev.json()["status"] == "verified"
    assert rev.json()["reviewer"] == "tester"


def test_admin_reject_rejects():
    v = _mk_venue()
    sub = client.post(
        "/api/claims/submit",
        json={"venue_id": v.id, "owner_name": "Eve", "email": "eve@example.com", "proof": ""},
    ).json()
    r = client.post(
        f"/api/admin/claims/{sub['claim_id']}/review",
        json={"action": "reject", "reviewer": "tester", "note": "no proof"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "rejected"


def test_owner_lookup_after_verification():
    v = _mk_venue()
    sub = client.post(
        "/api/claims/submit",
        json={"venue_id": v.id, "owner_name": "Fiona", "email": "fiona@example.com", "proof": ""},
    ).json()
    token = sub["magic_link"].rsplit("/", 1)[-1]
    client.get(f"/api/claims/verify/{token}")

    r = client.get(f"/api/venues/{v.id}/owner")
    assert r.status_code == 200
    owner = r.json()["owner"]
    assert owner and owner["email"] == "fiona@example.com"


def test_webhook_dispatcher_noop_when_unconfigured():
    """When no URL is set, dispatch is silent and recent log stays empty."""
    from app.services import webhooks as wh
    before = len(wh.recent_events(50))
    wh.dispatch("VENUE_CLAIMED", title="unit", body="no op", meta={"x": 1})
    import time; time.sleep(0.3)
    after = len(wh.recent_events(50))
    # No URL configured → dispatcher doesn't enqueue anything
    assert after == before


def test_webhook_dispatcher_fires_with_url(monkeypatch):
    """With an URL configured + test endpoint, dispatcher records success."""
    from app.services import webhooks as wh
    monkeypatch.setenv("WEBHOOK_VENUE_CLAIMED_URL", "https://httpbin.org/post")
    before = len(wh.recent_events(50))
    wh.dispatch("VENUE_CLAIMED", title="unit-live", body="real fire", meta={"k": 2})
    import time; time.sleep(6)
    events = wh.recent_events(50)
    assert len(events) > before
    latest = events[0]
    assert latest["event_type"] == "VENUE_CLAIMED"
    assert latest["title"] == "unit-live"
    assert latest["ok"] is True
