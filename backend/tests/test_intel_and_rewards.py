# -*- coding: utf-8 -*-
"""Iteration 7 additive tests — User Intelligence + Rewards APIs.

All additive. Does not touch existing endpoints.
"""
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
    assert r.status_code == 200, r.text
    items = r.json()["items"]
    assert items, "no venues seeded"
    return items[0]["venue"]["id"]


# ---------------------------------------------------------------------------
# Intel
# ---------------------------------------------------------------------------
def test_ping_records_location(session):
    r = session.post(
        f"{API}/intel/ping",
        json={"lat": 40.758, "lng": -73.9855, "device_id": "pytest-dev"},
        timeout=15,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["id"] and body["timestamp"]


def test_flow_returns_one_entry_per_venue(session):
    r = session.get(f"{API}/intel/flow", timeout=15)
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list) and len(body) >= 1
    row = body[0]
    assert set(row) >= {"venue_id", "name", "flow", "pings_now", "pings_past"}
    assert row["flow"] in {"rising", "peaking", "falling", "steady"}


def test_visit_detector_runs(session):
    r = session.post(f"{API}/intel/visits/detect", timeout=15)
    assert r.status_code == 200
    assert "created" in r.json()


def test_trajectory_snapshot_and_read(session, venue_id):
    snap = session.post(f"{API}/intel/trajectory/snapshot", timeout=15)
    assert snap.status_code == 200
    assert snap.json()["written"] >= 1
    r = session.get(f"{API}/intel/trajectory/{venue_id}?hours=1", timeout=15)
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list) and len(body) >= 1
    assert set(body[0]) == {"timestamp", "vibe_score"}


def test_trajectory_unknown_venue_is_404(session):
    r = session.get(f"{API}/intel/trajectory/nope-{uuid.uuid4()}", timeout=15)
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Rewards
# ---------------------------------------------------------------------------
def test_reward_rules(session):
    r = session.get(f"{API}/rewards/rules", timeout=15)
    assert r.status_code == 200
    rules = r.json()
    assert rules["feedback"] == 1
    assert rules["visit"] == 3


def test_earn_and_wallet_flow(session):
    uid = f"pytest-{uuid.uuid4()}"
    w0 = session.get(f"{API}/rewards/wallet/{uid}", timeout=15).json()
    assert w0["credits"] == 0

    earn = session.post(
        f"{API}/rewards/earn", json={"user_id": uid, "action": "feedback"}, timeout=15,
    ).json()
    assert earn["awarded"] == 1
    assert earn["credits"] == 1

    earn2 = session.post(
        f"{API}/rewards/earn", json={"user_id": uid, "action": "visit"}, timeout=15,
    ).json()
    assert earn2["credits"] == 4  # 1 + 3

    w1 = session.get(f"{API}/rewards/wallet/{uid}", timeout=15).json()
    assert w1["credits"] == 4


def test_earn_unknown_action_rejected(session):
    r = session.post(
        f"{API}/rewards/earn", json={"user_id": "x", "action": "__nope__"}, timeout=15,
    )
    assert r.status_code == 400


def test_offer_crud_and_redeem(session, venue_id):
    uid = f"pytest-{uuid.uuid4()}"

    # Stock the wallet with exactly 4 credits so redeeming twice will fail the 2nd time.
    session.post(f"{API}/rewards/earn", json={"user_id": uid, "amount": 4, "action": "seed"})

    # Create offer
    r = session.post(
        f"{API}/rewards/offers",
        json={"venue_id": venue_id, "name": "Pytest Offer", "cost_credits": 4},
        timeout=15,
    )
    assert r.status_code == 201, r.text
    offer = r.json()
    oid = offer["id"]

    # Redeem
    r = session.post(
        f"{API}/rewards/redeem", json={"user_id": uid, "offer_id": oid}, timeout=15,
    )
    assert r.status_code == 200, r.text
    rd = r.json()
    assert rd["cost_credits"] == 4
    assert rd["venue_id"] == venue_id

    # Insufficient credits second time
    r2 = session.post(
        f"{API}/rewards/redeem", json={"user_id": uid, "offer_id": oid}, timeout=15,
    )
    assert r2.status_code == 400

    # Deactivate
    d = session.delete(f"{API}/rewards/offers/{oid}", timeout=15)
    assert d.status_code == 200 and d.json()["active"] is False


def test_redemption_listing(session, venue_id):
    r = session.get(f"{API}/rewards/redemptions?venue_id={venue_id}", timeout=15)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_offer_for_unknown_venue_404(session):
    r = session.post(
        f"{API}/rewards/offers",
        json={"venue_id": "not-a-venue", "name": "x", "cost_credits": 1},
        timeout=15,
    )
    assert r.status_code == 404
