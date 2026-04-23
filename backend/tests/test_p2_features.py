# -*- coding: utf-8 -*-
"""Iteration 8 — P2 additive features: push, WS, Distance Matrix."""
from __future__ import annotations

import asyncio
import os
import uuid
from unittest.mock import patch

import pytest
import requests

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
API = f"{BASE_URL}/api"
# WebSockets are tested over the in-cluster localhost — the public
# preview ingress in some environments doesn't proxy `ws://`/`wss://`.
WS_URL = "ws://localhost:8001"


@pytest.fixture(scope="module")
def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def venue_id(session) -> str:
    r = session.get(f"{API}/admin/venues", timeout=30)
    assert r.status_code == 200, r.text
    items = r.json()["items"]
    assert items
    return items[0]["venue"]["id"]


# ---------------------------------------------------------------------------
# Push notifications
# ---------------------------------------------------------------------------
def test_push_register_persists(session):
    uid = f"push-{uuid.uuid4()}"
    r = session.post(
        f"{API}/notifications/register",
        json={"wallet_id": uid, "expo_push_token": "ExponentPushToken[test-xyz]"},
        timeout=15,
    )
    assert r.status_code == 200
    assert r.json() == {"wallet_id": uid, "registered": True}

    # Upsert with a new token
    r2 = session.post(
        f"{API}/notifications/register",
        json={"wallet_id": uid, "expo_push_token": "ExponentPushToken[updated]"},
        timeout=15,
    )
    assert r2.status_code == 200


def test_milestone_helper_computes_correctly():
    # Import here so the test is independent of the HTTP flow.
    from app.services.notifications import milestone_for
    assert milestone_for(9, 10) == 10
    assert milestone_for(0, 25) == 10   # first milestone crossed
    assert milestone_for(10, 24) is None
    assert milestone_for(49, 50) == 50
    assert milestone_for(99, 100) == 100
    assert milestone_for(100, 101) is None


def test_milestone_push_fired_on_earn(session, venue_id):
    uid = f"milestone-{uuid.uuid4()}"
    # Register a push token so the send path is attempted.
    session.post(
        f"{API}/notifications/register",
        json={"wallet_id": uid, "expo_push_token": "ExponentPushToken[milestone-test]"},
    )
    # Earn up to 9 credits — no milestone yet.
    for _ in range(9):
        session.post(f"{API}/rewards/earn", json={"user_id": uid, "action": "feedback"})
    # 10th credit should trigger milestone_for(9, 10) == 10.
    r = session.post(f"{API}/rewards/earn", json={"user_id": uid, "action": "feedback"})
    assert r.status_code == 200
    assert r.json()["credits"] == 10
    # The send itself hits Expo's URL with a fake token — we don't assert delivery,
    # only that the earn endpoint did not blow up on the push side-effect.


# ---------------------------------------------------------------------------
# Distance Matrix
# ---------------------------------------------------------------------------
def test_venues_list_enriches_with_travel_time_when_coords_provided(session):
    r = session.get(f"{API}/venues/list?user_lat=40.73&user_lng=-73.99", timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert data["count"] > 0
    first = data["items"][0]
    for k in ("distance_km", "walking_time_minutes", "driving_time_minutes", "travel_provider"):
        assert k in first
    assert first["travel_provider"] in ("stub", "google")
    assert first["walking_time_minutes"] >= 0


def test_venues_list_no_coords_omits_travel_time(session):
    r = session.get(f"{API}/venues/list", timeout=15)
    assert r.status_code == 200
    first = r.json()["items"][0]
    assert "walking_time_minutes" not in first


def test_intel_score_single_venue(session, venue_id):
    r = session.get(
        f"{API}/intel/score/{venue_id}?user_lat=40.73&user_lng=-73.99", timeout=15,
    )
    assert r.status_code == 200
    d = r.json()
    assert d["id"] == venue_id
    assert d["walking_time_minutes"] >= 0
    assert d["driving_time_minutes"] >= 0

    r404 = session.get(f"{API}/intel/score/nope-{uuid.uuid4()}", timeout=15)
    assert r404.status_code == 404


def test_distance_matrix_cache_is_warm():
    from app.services.maps import get_travel_time, clear_cache, CACHE_TTL_S

    clear_cache()
    a = get_travel_time(40.73, -73.99, 40.758, -73.9855)
    assert a["cached"] is False
    b = get_travel_time(40.73, -73.99, 40.758, -73.9855)
    assert b["cached"] is True
    assert b["walking_time_minutes"] == a["walking_time_minutes"]


def test_distance_matrix_fallback_stub_when_no_key():
    from app.services.maps import get_travel_time, clear_cache
    clear_cache()
    d = get_travel_time(40.73, -73.99, 40.77, -73.97)
    # With GOOGLE_MAPS_API_KEY unset in this environment, provider must be the stub.
    assert d["provider"] == "stub"
    assert d["distance_km"] > 0


# ---------------------------------------------------------------------------
# WebSocket — Vibe Pulse
# ---------------------------------------------------------------------------
def _run(coro):
    return asyncio.run(coro)


def test_ws_snapshot_on_connect(venue_id):
    import websockets

    async def go():
        async with websockets.connect(f"{WS_URL}/ws/vibe/{venue_id}") as ws:
            first = await asyncio.wait_for(ws.recv(), timeout=10)
            return first

    msg = _run(go())
    import json as _json
    payload = _json.loads(msg)
    assert payload["type"] == "snapshot"
    assert payload["venue_id"] == venue_id
    assert "vibe_score" in payload


def test_ws_broadcast_on_feedback(venue_id):
    import json as _json
    import websockets

    async def go():
        async with websockets.connect(f"{WS_URL}/ws/vibe/{venue_id}") as ws:
            await asyncio.wait_for(ws.recv(), timeout=10)   # snapshot
            # Fire feedback over HTTP (sync) while the socket is connected.
            requests.post(
                f"{API}/feedback",
                json={"venue_id": venue_id, "vote": "good"},
                timeout=15,
            )
            # Expect a vibe_update within a few seconds.
            for _ in range(6):
                try:
                    frame = await asyncio.wait_for(ws.recv(), timeout=2)
                except asyncio.TimeoutError:
                    continue
                p = _json.loads(frame)
                if p.get("type") == "vibe_update" and p.get("venue_id") == venue_id:
                    return p
            return None

    payload = _run(go())
    assert payload is not None, "did not receive a vibe_update frame after feedback"
    assert "vibe_score" in payload
    assert "external_signals" in payload
