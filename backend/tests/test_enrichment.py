# -*- coding: utf-8 -*-
"""Venue enrichment engine tests."""
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
    return session.get(f"{API}/admin/venues").json()["items"][0]["venue"]["id"]


def test_enrich_venue_returns_signals(session, venue_id):
    r = session.post(f"{API}/intel/enrich/{venue_id}?refresh=true", timeout=15)
    assert r.status_code == 200
    body = r.json()
    sig = body["signals"]
    for key in ("events", "travel", "social", "footfall", "derived"):
        assert key in sig, f"missing {key} in signals"
    assert body["cached"] is False


def test_enrich_soft_cache(session, venue_id):
    # Back-to-back (no refresh) should be cached.
    session.post(f"{API}/intel/enrich/{venue_id}?refresh=true", timeout=15)
    r2 = session.post(f"{API}/intel/enrich/{venue_id}?refresh=false", timeout=15)
    assert r2.json()["cached"] is True


def test_enrich_unknown_venue_404(session):
    r = session.post(f"{API}/intel/enrich/nope-{uuid.uuid4()}")
    assert r.status_code == 404


def test_enrich_all_scheduled_via_background(session):
    r = session.post(f"{API}/intel/enrich/all/run")
    assert r.status_code == 200
    assert r.json()["status"] == "scheduled"


def test_enrich_read_route(session, venue_id):
    session.post(f"{API}/intel/enrich/{venue_id}?refresh=true", timeout=15)
    r = session.get(f"{API}/intel/enrich/{venue_id}")
    assert r.status_code == 200
    assert "signals" in r.json()


def test_enrichment_degrades_without_keys(venue_id):
    """Even with NO external API keys, enrichment must return a full signal bundle."""
    from app.core.database import SessionLocal
    from app.services.enrichment import enrich_venue
    db = SessionLocal()
    try:
        r = enrich_venue(db, venue_id, refresh=True)
        sig = r["signals"]
        # Weather provider returns None when OPENWEATHER_API_KEY is unset — that's OK.
        assert sig["weather"] is None or isinstance(sig["weather"], dict)
        assert sig["social"]["source"] == "stub"
        assert sig["events"]["source"] in ("stub", "bandsintown_pending")
    finally:
        db.close()
