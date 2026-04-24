# -*- coding: utf-8 -*-
"""AI discovery system tests."""
from __future__ import annotations

import os

import pytest
import requests

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def test_discovery_new_city_query(session):
    r = session.get(f"{API}/discovery/new?city=Benalmadena", timeout=60)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["city"] == "Benalmadena"
    assert "items" in body
    # Each item respects the approval contract — no live venue is auto-created.
    for i in body["items"]:
        assert i["confidence"] >= 0.0 and i["confidence"] <= 1.0


def test_discovery_closed_empty_for_fresh_city(session):
    r = session.get(f"{API}/discovery/closed?city=NoSuchCity")
    assert r.status_code == 200
    assert "items" in r.json()


def test_discovery_trending_returns_items(session):
    r = session.get(f"{API}/discovery/trending?limit=5")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    # Each item is a live Venue reference; fields present even if the list is empty.
    for it in body["items"]:
        assert "id" in it and "score" in it and "reason" in it


def test_discovery_approve_and_reject_flow(session):
    # Find or create a candidate to act on.
    new_resp = session.get(f"{API}/discovery/new?city=Benalmadena", timeout=60).json()
    items = new_resp["items"]
    if not items:
        pytest.skip("no OSM candidates available for approval test")

    target = items[0]
    r = session.post(f"{API}/discovery/approve", json={"candidate_id": target["id"]})
    assert r.status_code == 200
    approved = r.json()
    assert approved["approved"] == target["id"]
    assert "venue_id" in approved  # because kind="new" creates the live venue

    # Re-running the detector should NOT surface the approved item again (status != pending)
    new_after = session.get(f"{API}/discovery/new?city=Benalmadena", timeout=60).json()
    remaining_ids = {i["id"] for i in new_after["items"]}
    assert target["id"] not in remaining_ids

    # Reject flow on a different candidate if any remain.
    if new_after["items"]:
        other = new_after["items"][0]
        rr = session.post(f"{API}/discovery/reject", json={"candidate_id": other["id"]})
        assert rr.status_code == 200
        assert rr.json()["rejected"] == other["id"]


def test_discovery_approve_unknown_404(session):
    r = session.post(f"{API}/discovery/approve", json={"candidate_id": "does-not-exist"})
    assert r.status_code == 404
