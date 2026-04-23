# -*- coding: utf-8 -*-
"""Vibe2Nite backend regression suite.

Runs against the live backend (supervisor managed, port 8001 via /api prefix).
Covers: health, recommendations (/vibes/top), feedback (/feedback),
admin CRUD + signal update, scoring correctness, branded docs, and OpenAPI.
"""
import math
import os
import re

import pytest
import requests

# Prefer REACT_APP_BACKEND_URL if available, otherwise fall back to local
# supervisor-hosted backend on 8001 (per agent_to_agent_context_note).
BASE_URL = (
    os.environ.get("REACT_APP_BACKEND_URL")
    or "http://localhost:8001"
).rstrip("/")

NYC_LAT = 40.73
NYC_LNG = -73.99

WEIGHTS = {
    "manual_score": 0.25,
    "social_activity": 0.25,
    "user_votes": 0.25,
    "time_prediction": 0.15,
    "venue_boost": 0.10,
}


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def all_venues(api):
    r = api.get(f"{BASE_URL}/api/admin/venues", timeout=10)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["count"] >= 12, f"expected >=12 seeded venues, got {data['count']}"
    return data["items"]


@pytest.fixture(scope="session")
def first_venue(all_venues):
    # deterministic: pick first venue
    return all_venues[0]


# --------------------------------------------------------------------------- #
# Health
# --------------------------------------------------------------------------- #
class TestHealth:
    def test_health_ok(self, api):
        r = api.get(f"{BASE_URL}/api/health", timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert body["service"] == "vibe2nite"
        assert "version" in body
        assert "time" in body


# --------------------------------------------------------------------------- #
# /vibes/top
# --------------------------------------------------------------------------- #
class TestVibesTop:
    def test_top_returns_three_slots(self, api, all_venues):
        r = api.get(
            f"{BASE_URL}/api/vibes/top",
            params={"lat": NYC_LAT, "lng": NYC_LNG},
            timeout=10,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        for key in ("best_overall", "live_music", "hidden_gem"):
            assert key in data
            assert data[key] is not None, f"{key} must not be null for NYC"
            assert data[key]["distance_km"] is not None
            assert data[key]["vibe"]["vibe_score"] is not None

        best = data["best_overall"]["vibe"]["vibe_score"]
        gem = data["hidden_gem"]["vibe"]["vibe_score"]
        # best_overall must be max score, hidden_gem must be min score across all
        # venues within radius (default 50km, seed is NYC).
        scores = [v["vibe"]["vibe_score"] for v in all_venues]
        assert math.isclose(best, max(scores), abs_tol=0.01), (best, max(scores))
        assert math.isclose(gem, min(scores), abs_tol=0.01), (gem, min(scores))

        # live_music must actually be live_music category (or equal best when fallback)
        lm_cat = data["live_music"]["venue"]["category"]
        assert lm_cat in ("live_music", "bar", "club", "cafe"), lm_cat

    def test_live_music_is_best_live_music_category(self, api, all_venues):
        r = api.get(
            f"{BASE_URL}/api/vibes/top",
            params={"lat": NYC_LAT, "lng": NYC_LNG},
            timeout=10,
        )
        data = r.json()
        lm_venues = [v for v in all_venues if v["venue"]["category"] == "live_music"]
        if lm_venues:
            top_lm_score = max(v["vibe"]["vibe_score"] for v in lm_venues)
            assert data["live_music"]["venue"]["category"] == "live_music"
            assert math.isclose(
                data["live_music"]["vibe"]["vibe_score"], top_lm_score, abs_tol=0.01
            )

    def test_live_music_fallback_to_best_overall(self, api):
        # Tiny radius centered at a non-live-music seeded venue location
        # "Local Tapas Spot" is a bar at (40.7250, -74.0020) — with 0.1km radius
        # only bar(s) may be in range, no live_music -> fallback to best_overall.
        r = api.get(
            f"{BASE_URL}/api/vibes/top",
            params={"lat": 40.7250, "lng": -74.0020, "radius_km": 0.1},
            timeout=10,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        if data["best_overall"] is None:
            pytest.skip("no venues in tiny radius; cannot test fallback here")
        assert data["live_music"] is not None
        # Fallback: when no live_music venue exists in range, live_music == best_overall
        lm_cat = data["live_music"]["venue"]["category"]
        if lm_cat != "live_music":
            assert (
                data["live_music"]["venue"]["id"]
                == data["best_overall"]["venue"]["id"]
            )

    def test_out_of_range_returns_all_null(self, api):
        # Middle of the Pacific — no venues within 50km.
        r = api.get(
            f"{BASE_URL}/api/vibes/top",
            params={"lat": 0.0, "lng": -160.0},
            timeout=10,
        )
        assert r.status_code == 200
        data = r.json()
        assert data == {
            "best_overall": None,
            "live_music": None,
            "hidden_gem": None,
        }

    def test_lat_out_of_range_422(self, api):
        r = api.get(
            f"{BASE_URL}/api/vibes/top",
            params={"lat": 95.0, "lng": 0.0},
            timeout=10,
        )
        assert r.status_code == 422

    def test_lng_out_of_range_422(self, api):
        r = api.get(
            f"{BASE_URL}/api/vibes/top",
            params={"lat": 0.0, "lng": 200.0},
            timeout=10,
        )
        assert r.status_code == 422


# --------------------------------------------------------------------------- #
# /feedback
# --------------------------------------------------------------------------- #
class TestFeedback:
    def test_busy_vote_updates_score(self, api, all_venues):
        target = all_venues[0]
        vid = target["venue"]["id"]
        before = target["vibe"]["vibe_score"]

        r = api.post(
            f"{BASE_URL}/api/feedback",
            json={"venue_id": vid, "vote": "busy"},
            timeout=10,
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["venue_id"] == vid
        assert "new_vibe_score" in body
        assert "new_crowd_level" in body
        assert body["new_crowd_level"] in ("busy", "medium", "dead")

        # Persistence: admin should reflect the new score
        admin = api.get(f"{BASE_URL}/api/admin/venues", timeout=10).json()
        updated = next(x for x in admin["items"] if x["venue"]["id"] == vid)
        assert math.isclose(
            updated["vibe"]["vibe_score"], body["new_vibe_score"], abs_tol=0.01
        )
        # A 'busy' vote should not decrease the score (user_votes was already 10
        # so it may stay flat due to cap — but never go down).
        assert updated["vibe"]["vibe_score"] >= before - 0.01

    def test_dead_lowers_and_good_raises(self, api, all_venues):
        # use a mid-score venue ("Velvet Underground Lounge")
        target = next(
            v for v in all_venues if v["venue"]["name"] == "Velvet Underground Lounge"
        )
        vid = target["venue"]["id"]

        s0 = api.get(f"{BASE_URL}/api/admin/venues").json()
        s0_score = next(
            x for x in s0["items"] if x["venue"]["id"] == vid
        )["vibe"]["vibe_score"]
        s0_uv = next(
            x for x in s0["items"] if x["venue"]["id"] == vid
        )["vibe"]["signals"]["user_votes"]

        # dead -> lowers
        api.post(
            f"{BASE_URL}/api/feedback",
            json={"venue_id": vid, "vote": "dead"},
            timeout=10,
        )
        s1 = api.get(f"{BASE_URL}/api/admin/venues").json()
        s1_uv = next(
            x for x in s1["items"] if x["venue"]["id"] == vid
        )["vibe"]["signals"]["user_votes"]
        s1_score = next(
            x for x in s1["items"] if x["venue"]["id"] == vid
        )["vibe"]["vibe_score"]

        # user_votes must stay within [0, 10]
        assert 0.0 <= s1_uv <= 10.0
        assert s1_uv <= s0_uv  # cannot go up
        if s0_uv > 0:
            assert s1_uv < s0_uv  # strictly lowered when not floored
            assert s1_score < s0_score

        # good -> raises (unless capped)
        api.post(
            f"{BASE_URL}/api/feedback",
            json={"venue_id": vid, "vote": "good"},
            timeout=10,
        )
        s2 = api.get(f"{BASE_URL}/api/admin/venues").json()
        s2_uv = next(
            x for x in s2["items"] if x["venue"]["id"] == vid
        )["vibe"]["signals"]["user_votes"]
        assert 0.0 <= s2_uv <= 10.0
        assert s2_uv >= s1_uv  # cannot go down after 'good'

    def test_invalid_vote_422(self, api, first_venue):
        r = api.post(
            f"{BASE_URL}/api/feedback",
            json={"venue_id": first_venue["venue"]["id"], "vote": "meh"},
            timeout=10,
        )
        assert r.status_code == 422

    def test_unknown_venue_404(self, api):
        r = api.post(
            f"{BASE_URL}/api/feedback",
            json={"venue_id": "00000000-0000-0000-0000-000000000000", "vote": "busy"},
            timeout=10,
        )
        assert r.status_code == 404


# --------------------------------------------------------------------------- #
# /admin
# --------------------------------------------------------------------------- #
class TestAdmin:
    def test_list_venues_shape(self, all_venues):
        assert len(all_venues) >= 12
        item = all_venues[0]
        assert "venue" in item and "vibe" in item
        for k in ("id", "name", "category", "latitude", "longitude"):
            assert k in item["venue"]
        for k in ("vibe_score", "crowd_level", "signals", "last_updated"):
            assert k in item["vibe"]
        for k in WEIGHTS.keys():
            assert k in item["vibe"]["signals"]

    def test_create_and_update_signals_recomputes_score(self, api):
        # CREATE
        payload = {
            "name": "TEST_The Vibe Lab",
            "category": "club",
            "latitude": 40.731,
            "longitude": -73.991,
        }
        r = api.post(f"{BASE_URL}/api/admin/venues", json=payload, timeout=10)
        assert r.status_code == 201, r.text
        created = r.json()
        assert created["name"] == payload["name"]
        assert created["category"] == payload["category"]
        vid = created["id"]

        # Appears in /admin/venues
        listing = api.get(f"{BASE_URL}/api/admin/venues").json()
        assert any(x["venue"]["id"] == vid for x in listing["items"])

        # PATCH signals and verify recomputation
        signals = {
            "manual_score": 8.0,
            "social_activity": 8.0,
            "time_prediction": 8.0,
            "venue_boost": 8.0,
        }
        r = api.patch(
            f"{BASE_URL}/api/admin/venues/{vid}/signals", json=signals, timeout=10
        )
        assert r.status_code == 200, r.text
        vibe = r.json()
        # user_votes defaults to 0 -> expected weighted sum
        # 8*.25 + 8*.25 + 0*.25 + 8*.15 + 8*.10 = 2 + 2 + 0 + 1.2 + 0.8 = 6.0
        assert math.isclose(vibe["vibe_score"], 6.0, abs_tol=0.01), vibe
        assert vibe["crowd_level"] == "medium"

        # Push to busy (>=8). Make user_votes 10 via signals update? user_votes
        # isn't exposed in PATCH. Instead use max signals.
        r = api.patch(
            f"{BASE_URL}/api/admin/venues/{vid}/signals",
            json={
                "manual_score": 10.0,
                "social_activity": 10.0,
                "time_prediction": 10.0,
                "venue_boost": 10.0,
            },
            timeout=10,
        )
        vibe2 = r.json()
        # 10*.25 + 10*.25 + 0*.25 + 10*.15 + 10*.10 = 2.5+2.5+0+1.5+1.0 = 7.5
        assert math.isclose(vibe2["vibe_score"], 7.5, abs_tol=0.01)
        assert vibe2["crowd_level"] == "medium"

        # Now push user_votes via POST /feedback busy votes to cross 8
        for _ in range(10):
            api.post(
                f"{BASE_URL}/api/feedback",
                json={"venue_id": vid, "vote": "busy"},
                timeout=10,
            )
        listing = api.get(f"{BASE_URL}/api/admin/venues").json()
        final = next(x for x in listing["items"] if x["venue"]["id"] == vid)
        # signals: all 10 -> score 10 -> busy
        assert final["vibe"]["vibe_score"] >= 8.0 - 0.01
        assert final["vibe"]["vibe_score"] <= 10.0 + 0.01
        assert final["vibe"]["crowd_level"] == "busy"

    def test_update_signals_unknown_id_404(self, api):
        r = api.patch(
            f"{BASE_URL}/api/admin/venues/00000000-0000-0000-0000-000000000000/signals",
            json={"manual_score": 5.0},
            timeout=10,
        )
        assert r.status_code == 404


# --------------------------------------------------------------------------- #
# Scoring math
# --------------------------------------------------------------------------- #
class TestScoringMath:
    def test_seeded_scores_match_weighted_formula(self, all_venues):
        for item in all_venues:
            s = item["vibe"]["signals"]
            expected = (
                s["manual_score"] * WEIGHTS["manual_score"]
                + s["social_activity"] * WEIGHTS["social_activity"]
                + s["user_votes"] * WEIGHTS["user_votes"]
                + s["time_prediction"] * WEIGHTS["time_prediction"]
                + s["venue_boost"] * WEIGHTS["venue_boost"]
            )
            expected = min(max(expected, 0.0), 10.0)
            actual = item["vibe"]["vibe_score"]
            assert math.isclose(actual, round(expected, 2), abs_tol=0.01), (
                item["venue"]["name"], actual, expected
            )

    def test_crowd_level_bands(self, all_venues):
        for item in all_venues:
            score = item["vibe"]["vibe_score"]
            crowd = item["vibe"]["crowd_level"]
            if score >= 8:
                assert crowd == "busy", (score, crowd)
            elif score >= 5:
                assert crowd == "medium", (score, crowd)
            else:
                assert crowd == "dead", (score, crowd)


# --------------------------------------------------------------------------- #
# Branded docs + OpenAPI
# --------------------------------------------------------------------------- #
class TestDocs:
    def test_branded_docs_html(self, api):
        r = api.get(f"{BASE_URL}/api/docs", timeout=10)
        assert r.status_code == 200
        assert "text/html" in r.headers.get("content-type", "")
        html = r.text
        assert "/api/static/vibe2nite.css" in html, "brand CSS missing from docs"
        assert "/api/openapi.json" in html, "openapi url missing"

    def test_static_css_served(self, api):
        r = api.get(f"{BASE_URL}/api/static/vibe2nite.css", timeout=10)
        assert r.status_code == 200
        assert len(r.text) > 0

    def test_openapi_schema(self, api):
        r = api.get(f"{BASE_URL}/api/openapi.json", timeout=10)
        assert r.status_code == 200
        schema = r.json()
        assert "openapi" in schema
        assert "paths" in schema
        for path in (
            "/api/vibes/top",
            "/api/feedback",
            "/api/admin/venues",
            "/api/health",
        ):
            assert path in schema["paths"], f"missing path: {path}"
