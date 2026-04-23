# -*- coding: utf-8 -*-
"""Signal Engine specific regression tests.

Covers:
- New POST /api/admin/signals/refresh endpoint + shape
- external_signals present on /api/admin/venues
- calculate_vibe_score_from_signals correctness vs reported vibe_score
- Scheduler populates signals at startup (external_signals not null)
- Jitter between two refreshes produces at least one score diff
- compute_vibe_score (legacy) still importable and works
"""
import math
import os
import time

import pytest
import requests

BASE_URL = (
    os.environ.get("REACT_APP_BACKEND_URL") or "http://localhost:8001"
).rstrip("/")

EXT_KEYS = {
    "google_score",
    "social_score",
    "event_score",
    "time_score",
    "user_votes_score",
    "updated_at",
}


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def venues(api):
    r = api.get(f"{BASE_URL}/api/admin/venues", timeout=15)
    assert r.status_code == 200, r.text
    d = r.json()
    # If any venue has no external_signals, trigger manual refresh once.
    if any(x.get("external_signals") is None for x in d["items"]):
        api.post(f"{BASE_URL}/api/admin/signals/refresh", timeout=30)
        r = api.get(f"{BASE_URL}/api/admin/venues", timeout=15)
        d = r.json()
    return d


class TestSignalRefreshEndpoint:
    def test_refresh_returns_expected_shape(self, api):
        r = api.post(f"{BASE_URL}/api/admin/signals/refresh", timeout=60)
        assert r.status_code == 200, r.text
        body = r.json()
        # Accept {status, refreshed, errors, total} OR {status:"already_running"}
        assert "status" in body
        if body["status"] == "already_running":
            pytest.skip("prior refresh still in flight")
        for k in ("refreshed", "errors", "total"):
            assert k in body, (k, body)
        assert body["total"] >= 12
        assert body["errors"] == 0
        assert body["refreshed"] == body["total"]

    def test_every_venue_has_external_signals_after_refresh(self, api):
        api.post(f"{BASE_URL}/api/admin/signals/refresh", timeout=60)
        r = api.get(f"{BASE_URL}/api/admin/venues", timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert d["count"] >= 12
        for item in d["items"]:
            ext = item.get("external_signals")
            assert ext is not None, item["venue"]["name"]
            assert set(ext.keys()) == EXT_KEYS, ext.keys()
            for k in ("google_score", "social_score", "event_score",
                      "time_score", "user_votes_score"):
                v = ext[k]
                assert isinstance(v, (int, float))
                assert 0.0 <= v <= 10.0 + 1e-6, (k, v)


class TestAdminVenuesShape:
    def test_shape_includes_external_signals(self, venues):
        assert venues["count"] >= 12
        for item in venues["items"]:
            assert set(item.keys()) >= {"venue", "vibe", "external_signals"}
            ext = item["external_signals"]
            assert ext is not None
            assert set(ext.keys()) == EXT_KEYS


class TestScoreFromSignals:
    def test_reported_vibe_score_matches_formula(self, venues):
        """Recompute score with manual_score*.25 + social*.25 + votes*.25 +
        time*.15 + boost*.10 using external_signals + vibe.signals.manual_score
        and vibe.signals.venue_boost. Must be within 0.02."""
        failures = []
        for item in venues["items"]:
            ext = item["external_signals"]
            vsig = item["vibe"]["signals"]
            expected = (
                vsig["manual_score"] * 0.25
                + ext["social_score"] * 0.25
                + ext["user_votes_score"] * 0.25
                + ext["time_score"] * 0.15
                + vsig["venue_boost"] * 0.10
            )
            expected = round(min(max(expected, 0.0), 10.0), 2)
            actual = item["vibe"]["vibe_score"]
            if not math.isclose(actual, expected, abs_tol=0.02):
                failures.append(
                    (item["venue"]["name"], actual, expected)
                )
        assert not failures, failures


class TestScoreChangesBetweenRefreshes:
    def test_jitter_between_two_refreshes(self, api):
        r1 = api.post(f"{BASE_URL}/api/admin/signals/refresh", timeout=60).json()
        if r1.get("status") == "already_running":
            time.sleep(1)
        snap1 = api.get(f"{BASE_URL}/api/admin/venues").json()["items"]
        scores1 = {x["venue"]["id"]: x["vibe"]["vibe_score"] for x in snap1}

        # live_jitter is a 5-min sine; need at least a few seconds for a
        # visible change after rounding to 2dp.
        time.sleep(8)

        r2 = api.post(f"{BASE_URL}/api/admin/signals/refresh", timeout=60).json()
        if r2.get("status") == "already_running":
            time.sleep(2)
            api.post(f"{BASE_URL}/api/admin/signals/refresh", timeout=60).json()
        snap2 = api.get(f"{BASE_URL}/api/admin/venues").json()["items"]
        scores2 = {x["venue"]["id"]: x["vibe"]["vibe_score"] for x in snap2}

        diffs = sum(1 for vid, s in scores1.items() if scores2.get(vid) != s)
        assert diffs >= 1, (
            f"no venue score changed between refreshes (live_jitter missing?)"
            f" scores1={scores1} scores2={scores2}"
        )


class TestScoringModule:
    def test_legacy_compute_vibe_score_still_works(self):
        from app.services.scoring import compute_vibe_score
        sample = {
            "manual_score": 8.0,
            "social_activity": 8.0,
            "user_votes": 0.0,
            "time_prediction": 8.0,
            "venue_boost": 8.0,
        }
        # 8*.25 + 8*.25 + 0*.25 + 8*.15 + 8*.10 = 6.0
        assert math.isclose(compute_vibe_score(sample), 6.0, abs_tol=0.01)

    def test_calculate_vibe_score_from_signals_dict(self):
        from app.services.scoring import calculate_vibe_score_from_signals
        ext = {
            "social_score": 6.0,
            "user_votes_score": 4.0,
            "time_score": 5.0,
            "google_score": 7.0,     # unused in the formula
            "event_score": 7.0,      # unused in the formula
        }
        # 8*.25 + 6*.25 + 4*.25 + 5*.15 + 3*.10 = 2 + 1.5 + 1 + 0.75 + 0.3 = 5.55
        got = calculate_vibe_score_from_signals(ext, manual_score=8.0, venue_boost=3.0)
        assert math.isclose(got, 5.55, abs_tol=0.01), got
