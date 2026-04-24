# -*- coding: utf-8 -*-
"""Iteration 10 — P2 finish (push engine + inbox) and P3 (forecast, tourist-trap, gems, launch)."""
from __future__ import annotations

import os
import uuid

import pytest
import requests

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def venue_id(session) -> str:
    r = session.get(f"{API}/admin/venues", timeout=30)
    assert r.status_code == 200
    return r.json()["items"][0]["venue"]["id"]


# ---------------------------------------------------------------------------
# Push engine
# ---------------------------------------------------------------------------
def test_trigger_test_daily_login_records_inbox(session):
    uid = f"push-{uuid.uuid4()}"
    session.post(
        f"{API}/notifications/register",
        json={"wallet_id": uid, "expo_push_token": "ExponentPushToken[test]"},
    )
    r = session.post(
        f"{API}/notifications/trigger/test",
        json={"kind": "daily_login", "wallet_id": uid},
    )
    assert r.status_code == 200
    inbox = session.get(f"{API}/notifications/inbox/{uid}").json()["items"]
    assert len(inbox) >= 1
    assert inbox[0]["kind"] == "daily_login"


def test_trigger_test_vibe_spike_requires_venue(session):
    r = session.post(f"{API}/notifications/trigger/test", json={"kind": "vibe_spike"})
    assert r.status_code == 400


def test_trigger_test_vibe_spike_happy_path(session, venue_id):
    uid = f"push-{uuid.uuid4()}"
    session.post(
        f"{API}/notifications/register",
        json={"wallet_id": uid, "expo_push_token": "ExponentPushToken[test]"},
    )
    r = session.post(
        f"{API}/notifications/trigger/test",
        json={"kind": "vibe_spike", "wallet_id": uid, "venue_id": venue_id, "score": 9.4},
    )
    assert r.status_code == 200


def test_scan_spikes_endpoint(session):
    r = session.post(f"{API}/notifications/scan/spikes")
    assert r.status_code == 200
    # Either "dispatched" (sync) or "status: scheduled" (async) is acceptable.
    body = r.json()
    assert "dispatched" in body or body.get("status") == "scheduled"


def test_offer_drop_fires_push(session, venue_id):
    uid = f"push-{uuid.uuid4()}"
    session.post(
        f"{API}/notifications/register",
        json={"wallet_id": uid, "expo_push_token": "ExponentPushToken[test]"},
    )
    r = session.post(
        f"{API}/rewards/offers",
        json={"venue_id": venue_id, "name": "Pytest Offer Drop", "cost_credits": 5},
    )
    assert r.status_code == 201
    # The inbox should now contain an offer_drop row for this wallet.
    inbox = session.get(f"{API}/notifications/inbox/{uid}").json()["items"]
    kinds = [i["kind"] for i in inbox]
    assert "offer_drop" in kinds


# ---------------------------------------------------------------------------
# Forecast
# ---------------------------------------------------------------------------
def test_forecast_shape_and_cache(session, venue_id):
    # Force a fresh computation.
    first = session.get(f"{API}/forecast/{venue_id}?refresh=true", timeout=15).json()
    for k in ("current_score", "forecast_score", "trend", "confidence", "baseline", "momentum"):
        assert k in first
    assert 0.0 <= first["confidence"] <= 1.0
    assert first["trend"] in {"rising", "falling", "steady", "peaking"}
    assert first["cached"] is False

    second = session.get(f"{API}/forecast/{venue_id}", timeout=15).json()
    assert second["cached"] is True
    assert second["forecast_score"] == first["forecast_score"]


def test_forecast_404(session):
    r = session.get(f"{API}/forecast/does-not-exist-{uuid.uuid4()}")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Tourist-trap classifier + local gems
# ---------------------------------------------------------------------------
def test_tourist_flags_has_persisted_rows(session):
    r = session.get(f"{API}/intel/tourist-flags")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) > 0
    first = items[0]
    assert first["label"] in {"tourist_trap", "local_gem", "neutral"}
    assert -1.0 <= first["score"] <= 1.0


def test_tourist_flags_refresh_endpoint(session):
    r = session.post(f"{API}/intel/tourist-flags/refresh")
    assert r.status_code == 200
    assert len(r.json()["items"]) > 0


def test_local_gems_endpoint(session):
    r = session.get(f"{API}/intel/local-gems?limit=5")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) <= 5
    for g in items:
        assert g["label"] in {"local_gem", "neutral"}  # never tourist_trap
        assert "rank" in g


# ---------------------------------------------------------------------------
# Launch — city seed + onboard
# ---------------------------------------------------------------------------
def test_city_seed_creates_and_updates(session):
    unique = f"Pytest Venue {uuid.uuid4().hex[:8]}"
    payload = {
        "city": "Pytest City",
        "venues": [{
            "name": unique, "category": "bar",
            "latitude": 36.6, "longitude": -4.5,
            "music_type": "jazz", "price_level": 2, "age_group": "18+",
            "dress_code": "casual", "opening_hours": {"fri": "20:00-02:00"},
            "photos": ["https://example.com/p.jpg"],
        }],
    }
    r = session.post(f"{API}/city/seed", json=payload)
    assert r.status_code == 200, r.text
    first = r.json()
    assert first["created"] == 1
    # Re-run → updated (not created) because the name already exists.
    r2 = session.post(f"{API}/city/seed", json=payload)
    assert r2.json()["updated"] == 1


def test_venue_onboarding_and_login(session, venue_id):
    uname = f"owner_{uuid.uuid4().hex[:8]}"
    pwd = "vibepass1"

    r = session.post(
        f"{API}/venues/onboard",
        json={"venue_id": venue_id, "username": uname, "password": pwd},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == uname
    assert len(data["api_key"]) >= 16
    assert set(data["qr_codes"].keys()) == {"check_in", "feedback", "follow_venue"}
    assert data["qr_codes"]["check_in"].startswith("data:image/png;base64,")

    # Duplicate username rejected
    r2 = session.post(
        f"{API}/venues/onboard",
        json={"venue_id": venue_id, "username": uname, "password": pwd},
    )
    assert r2.status_code == 400

    # Login
    r3 = session.post(f"{API}/venues/login", json={"username": uname, "password": pwd})
    assert r3.status_code == 200
    assert r3.json()["api_key"] == data["api_key"]

    # Wrong password
    r4 = session.post(f"{API}/venues/login", json={"username": uname, "password": "wrong"})
    assert r4.status_code == 401


def test_onboard_unknown_venue_400(session):
    r = session.post(
        f"{API}/venues/onboard",
        json={"venue_id": "does-not-exist", "username": f"x_{uuid.uuid4().hex[:6]}", "password": "secret12"},
    )
    assert r.status_code == 400
