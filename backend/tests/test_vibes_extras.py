# -*- coding: utf-8 -*-
"""Iteration 5 additive tests — /api/vibes/* extras.

Covers directions, heatmap, live-music, tourist-flags, forecast and top3.
Regression for existing endpoints handled by backend_test.py and
test_feedback_propagation.py (kept untouched).
"""
from __future__ import annotations

import math
import os
from typing import Any, Dict, List

import pytest
import requests

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
API = f"{BASE_URL}/api"


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    # Ensure external signals are populated before any test runs.
    r = s.post(f"{API}/admin/signals/refresh", timeout=30)
    assert r.status_code == 200, r.text
    return s


@pytest.fixture(scope="module")
def venues(session) -> List[Dict[str, Any]]:
    """Flatten /admin/venues into a list of dicts with top-level id/lat/lng/external_signals."""
    r = session.get(f"{API}/admin/venues", timeout=30)
    assert r.status_code == 200, r.text
    payload = r.json()
    raw = payload["items"] if isinstance(payload, dict) else payload
    items = []
    for row in raw:
        v = row.get("venue", row)
        items.append({
            "id": v["id"],
            "name": v["name"],
            "category": v["category"],
            "latitude": v["latitude"],
            "longitude": v["longitude"],
            "vibe_score": (row.get("vibe") or {}).get("vibe_score"),
            "external_signals": row.get("external_signals") or {},
            "_raw": row,
        })
    assert items, "need at least 1 venue seeded"
    return items


@pytest.fixture(scope="module")
def first_venue(venues):
    return venues[0]


# ---------------------------------------------------------------------------
# regression — existing endpoints still green
# ---------------------------------------------------------------------------
class TestRegression:
    def test_health(self, session):
        r = session.get(f"{API}/health", timeout=10)
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_top(self, session, first_venue):
        r = session.get(
            f"{API}/vibes/top",
            params={"lat": first_venue["latitude"], "lng": first_venue["longitude"]},
            timeout=10,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        # /vibes/top response exposes best_overall / live_music / hidden_gem buckets.
        for key in ("best_overall", "live_music", "hidden_gem"):
            assert key in data, f"missing {key} in /vibes/top"

    def test_admin_venues_has_external_signals(self, venues):
        v = venues[0]["_raw"]
        assert "external_signals" in v, "external_signals missing on /admin/venues"

    def test_feedback_matches_next_get(self, session, first_venue):
        vid = first_venue["id"]
        r = session.post(
            f"{API}/feedback",
            json={"venue_id": vid, "vote": "good"},
            timeout=15,
        )
        assert r.status_code == 200, r.text
        new_score = r.json()["new_vibe_score"]
        # GET to verify propagation
        r2 = session.get(f"{API}/admin/venues", timeout=15)
        items = r2.json()["items"] if isinstance(r2.json(), dict) else r2.json()
        row = next(x for x in items if (x.get("venue", x)).get("id") == vid)
        current = row["vibe"]["vibe_score"] if "vibe" in row else row["vibe_score"]
        assert math.isclose(new_score, current, abs_tol=0.05), (new_score, current)

    def test_feedback_422_bad_vote(self, session, first_venue):
        r = session.post(
            f"{API}/feedback",
            json={"venue_id": first_venue["id"], "vote": "terrible"},
            timeout=10,
        )
        assert r.status_code == 422

    def test_feedback_404_unknown_venue(self, session):
        r = session.post(
            f"{API}/feedback",
            json={"venue_id": "does-not-exist", "vote": "good"},
            timeout=10,
        )
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# 1. directions
# ---------------------------------------------------------------------------
class TestDirections:
    def test_happy_path(self, session, first_venue):
        vid = first_venue["id"]
        lat = first_venue["latitude"] + 0.01
        lng = first_venue["longitude"] + 0.01
        r = session.get(
            f"{API}/vibes/directions",
            params={"venue_id": vid, "user_lat": lat, "user_lng": lng},
            timeout=10,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        for key in ("venue_id", "duration_minutes", "distance_meters", "deeplink", "provider"):
            assert key in d
        assert d["venue_id"] == vid
        assert d["provider"] == "stub"  # no GOOGLE_MAPS_API_KEY
        assert d["duration_minutes"] >= 1
        assert d["distance_meters"] >= 0
        assert d["deeplink"].startswith("https://www.google.com/maps/dir/?api=1")
        assert "travelmode=walking" in d["deeplink"]
        assert f"origin={lat}" in d["deeplink"] or f"origin={round(lat,6)}" in d["deeplink"]

    def test_404_unknown_venue(self, session):
        r = session.get(
            f"{API}/vibes/directions",
            params={"venue_id": "nope", "user_lat": 0, "user_lng": 0},
            timeout=10,
        )
        assert r.status_code == 404

    def test_422_out_of_range_lat(self, session, first_venue):
        r = session.get(
            f"{API}/vibes/directions",
            params={"venue_id": first_venue["id"], "user_lat": 200, "user_lng": 0},
            timeout=10,
        )
        assert r.status_code == 422

    def test_422_out_of_range_lng(self, session, first_venue):
        r = session.get(
            f"{API}/vibes/directions",
            params={"venue_id": first_venue["id"], "user_lat": 0, "user_lng": 500},
            timeout=10,
        )
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# 2. heatmap
# ---------------------------------------------------------------------------
class TestHeatmap:
    def test_shape_and_sort(self, session):
        r = session.get(f"{API}/vibes/heatmap", timeout=10)
        assert r.status_code == 200, r.text
        d = r.json()
        assert "count" in d and "points" in d
        assert d["count"] == len(d["points"])
        pts = d["points"]
        assert pts, "expected at least 1 point"
        heats = [p["heat"] for p in pts]
        assert heats == sorted(heats, reverse=True), "points must be sorted desc by heat"
        for p in pts:
            for k in ("id", "name", "category", "lat", "lng", "heat"):
                assert k in p
            assert 0.0 <= p["heat"] <= 10.0

    def test_formula_matches_external_signals(self, session):
        # Refresh + re-read admin/venues + heatmap as close together as possible
        # so the scheduler's 20s jitter doesn't skew the comparison.
        session.post(f"{API}/admin/signals/refresh", timeout=30)
        venues_now = session.get(f"{API}/admin/venues", timeout=10).json()["items"]
        heat = session.get(f"{API}/vibes/heatmap", timeout=10).json()
        pts = {p["id"]: p for p in heat["points"]}
        checked = 0
        for row in venues_now:
            v = row.get("venue", row)
            ext = row.get("external_signals") or {}
            if not ext:
                continue
            expected = (
                0.4 * float(ext.get("google_score", 0) or 0)
                + 0.3 * float(ext.get("social_score", 0) or 0)
                + 0.2 * float(ext.get("user_votes_score", 0) or 0)
                + 0.1 * float(ext.get("event_score", 0) or 0)
            )
            expected = min(10.0, max(0.0, expected))
            got = pts[v["id"]]["heat"]
            # abs_tol=0.3 absorbs the scheduler's ±20s live_jitter that may fire between
            # the admin/venues read and the heatmap read.
            assert math.isclose(got, expected, abs_tol=0.3), (v["id"], got, expected)
            checked += 1
        assert checked > 0

    def test_category_filter(self, session):
        r = session.get(
            f"{API}/vibes/heatmap",
            params=[("categories", "live_music"), ("categories", "club")],
            timeout=10,
        )
        assert r.status_code == 200
        for p in r.json()["points"]:
            assert p["category"] in {"live_music", "club"}


# ---------------------------------------------------------------------------
# 3. live-music
# ---------------------------------------------------------------------------
class TestLiveMusic:
    def test_flagged_shape(self, session):
        r = session.get(f"{API}/vibes/live-music", timeout=10)
        assert r.status_code == 200
        d = r.json()
        assert "count" in d and "items" in d
        assert d["count"] == len(d["items"])
        for it in d["items"]:
            for k in (
                "venue_id", "name", "category", "lat", "lng",
                "live_music", "confidence", "event_score", "vibe_score", "reason",
            ):
                assert k in it
            assert 0.0 <= it["confidence"] <= 1.0
            # must satisfy flag rule
            assert (it["category"] == "live_music" and it["event_score"] >= 3.0) or it["event_score"] >= 6.5

    def test_include_all(self, session, venues):
        r = session.get(f"{API}/vibes/live-music", params={"include_all": "true"}, timeout=10)
        assert r.status_code == 200
        d = r.json()
        assert d["count"] == len(venues), (d["count"], len(venues))


# ---------------------------------------------------------------------------
# 4. tourist-flags
# ---------------------------------------------------------------------------
class TestTouristFlags:
    def test_shape_and_rules(self, session, venues):
        r = session.get(f"{API}/vibes/tourist-flags", timeout=10)
        assert r.status_code == 200
        d = r.json()
        assert d["count"] == len(d["items"]) == len(venues)
        assert set(d["buckets"].keys()) == {"tourist_trap", "local_gem", "neutral"}
        assert sum(d["buckets"].values()) == d["count"]
        for it in d["items"]:
            label = it["label"]
            sig = it["signals"]
            g, s, v = sig["google_score"], sig["social_score"], sig["user_votes_score"]
            if label == "tourist_trap":
                assert g >= 7.0 and s <= 4.0 and v <= 4.0, (it, g, s, v)
            elif label == "local_gem":
                assert s >= 7.0 and v >= 7.0 and 4.0 <= g <= 7.0, (it, g, s, v)
            else:
                assert label == "neutral"


# ---------------------------------------------------------------------------
# 5. forecast
# ---------------------------------------------------------------------------
class TestForecast:
    def test_list(self, session, venues):
        r = session.get(f"{API}/vibes/forecast", timeout=10)
        assert r.status_code == 200
        d = r.json()
        assert d["count"] == len(d["items"]) == len(venues)
        allowed = {"rising", "peaking", "falling", "steady"}
        for it in d["items"]:
            for k in ("venue_id", "name", "trend", "delta_next_hour", "current_vibe_score", "as_of"):
                assert k in it
            assert it["trend"] in allowed

    def test_single(self, session, first_venue):
        r = session.get(f"{API}/vibes/forecast", params={"venue_id": first_venue["id"]}, timeout=10)
        assert r.status_code == 200
        d = r.json()
        assert d["venue_id"] == first_venue["id"]
        assert d["trend"] in {"rising", "peaking", "falling", "steady"}

    def test_single_404(self, session):
        r = session.get(f"{API}/vibes/forecast", params={"venue_id": "nope"}, timeout=10)
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# 6. top3
# ---------------------------------------------------------------------------
class TestTop3:
    def test_default(self, session):
        r = session.get(f"{API}/vibes/top3", timeout=10)
        assert r.status_code == 200
        d = r.json()
        assert len(d["items"]) <= 3
        for it in d["items"]:
            for k in (
                "id", "name", "category", "vibe_score",
                "adjusted_score", "lat", "lng", "distance_km", "tourist_label",
            ):
                assert k in it
            assert it["distance_km"] is None  # no user coords given
            assert math.isclose(it["adjusted_score"], it["vibe_score"], abs_tol=0.01) or \
                   it["tourist_label"] == "tourist_trap"  # tourist penalty may apply

    def test_vibe_filter_live_music(self, session):
        r = session.get(f"{API}/vibes/top3", params={"vibe": "live_music"}, timeout=10)
        assert r.status_code == 200
        for it in r.json()["items"]:
            assert it["category"] == "live_music"

    def test_avoid_tourist_traps(self, session):
        r = session.get(f"{API}/vibes/top3", params={"avoid_tourist_traps": "true"}, timeout=10)
        assert r.status_code == 200
        for it in r.json()["items"]:
            assert it["tourist_label"] != "tourist_trap"

    def test_distance_penalty(self, session, first_venue):
        # Use far-away coords so distance is large and penalty noticeable.
        lat = first_venue["latitude"] + 1.0  # ~111 km
        lng = first_venue["longitude"]
        r = session.get(
            f"{API}/vibes/top3",
            params={"user_lat": lat, "user_lng": lng},
            timeout=10,
        )
        assert r.status_code == 200
        for it in r.json()["items"]:
            assert it["distance_km"] is not None and it["distance_km"] >= 0
            expected = it["vibe_score"] - 0.05 * it["distance_km"]
            # tourist penalty applies if label==tourist_trap
            if it["tourist_label"] == "tourist_trap":
                expected -= 2.0
            expected = max(0.0, min(10.0, expected))
            assert math.isclose(it["adjusted_score"], expected, abs_tol=0.05), (it, expected)

    def test_radius_excludes(self, session, first_venue):
        lat = first_venue["latitude"] + 10.0  # ~1110 km away
        lng = first_venue["longitude"]
        r = session.get(
            f"{API}/vibes/top3",
            params={"user_lat": lat, "user_lng": lng, "radius_km": 1.0},
            timeout=10,
        )
        assert r.status_code == 200
        assert r.json()["count"] == 0
