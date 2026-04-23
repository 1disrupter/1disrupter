# -*- coding: utf-8 -*-
"""Regression tests for the iteration_4 fix.

After POST /api/feedback the service triggers scheduler.refresh_venue_signals
for that venue, so the response's `new_vibe_score` must equal the score a
subsequent GET /api/admin/venues reports.

Also validates user_feedback_signal (last-2h FeedbackLog window):
- 5 'dead' votes drop user_votes_score toward 0
- 5 'busy' votes climb it toward 10
"""
from __future__ import annotations

import math
import os
import sys

import pytest
import requests

# Make the backend package importable for direct DB cleanup.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal  # noqa: E402
from app.models import FeedbackLog  # noqa: E402

BASE_URL = (
    os.environ.get("REACT_APP_BACKEND_URL") or "http://localhost:8001"
).rstrip("/")


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture
def clean_venue(api):
    """Create a fresh venue and wipe all feedback_log rows so the 2h window
    is clean. Returns the venue_id."""
    payload = {
        "name": "TEST_Propagation_Venue",
        "category": "bar",
        "latitude": 40.735,
        "longitude": -73.995,
    }
    r = api.post(f"{BASE_URL}/api/admin/venues", json=payload, timeout=10)
    assert r.status_code == 201, r.text
    vid = r.json()["id"]

    # Wipe feedback_log globally (spec: DELETE FROM feedback_log).
    db = SessionLocal()
    try:
        db.query(FeedbackLog).delete()
        db.commit()
    finally:
        db.close()

    # Prime external_signals for this venue.
    api.post(f"{BASE_URL}/api/admin/signals/refresh", timeout=60)
    yield vid


def _get_venue(api, vid: str) -> dict:
    r = api.get(f"{BASE_URL}/api/admin/venues", timeout=10)
    assert r.status_code == 200
    return next(x for x in r.json()["items"] if x["venue"]["id"] == vid)


class TestFeedbackPropagation:
    """new_vibe_score in POST /feedback must equal subsequent GET score."""

    @pytest.mark.parametrize("vote", ["busy", "good", "dead"])
    def test_feedback_response_matches_published_score(self, api, clean_venue, vote):
        vid = clean_venue
        r = api.post(
            f"{BASE_URL}/api/feedback",
            json={"venue_id": vid, "vote": vote},
            timeout=15,
        )
        assert r.status_code == 200, r.text
        body = r.json()
        new_score = body["new_vibe_score"]
        assert isinstance(new_score, (int, float))
        assert 0.0 <= new_score <= 10.0

        fetched = _get_venue(api, vid)
        assert math.isclose(
            fetched["vibe"]["vibe_score"], new_score, abs_tol=0.02
        ), (vote, new_score, fetched["vibe"]["vibe_score"])

    def test_published_score_matches_new_formula(self, api, clean_venue):
        vid = clean_venue
        r = api.post(
            f"{BASE_URL}/api/feedback",
            json={"venue_id": vid, "vote": "busy"},
            timeout=15,
        )
        assert r.status_code == 200
        fetched = _get_venue(api, vid)
        ext = fetched["external_signals"]
        vsig = fetched["vibe"]["signals"]
        expected = (
            vsig["manual_score"] * 0.25
            + ext["social_score"] * 0.25
            + ext["user_votes_score"] * 0.25
            + ext["time_score"] * 0.15
            + vsig["venue_boost"] * 0.10
        )
        expected = round(min(max(expected, 0.0), 10.0), 2)
        assert math.isclose(
            fetched["vibe"]["vibe_score"], expected, abs_tol=0.02
        ), (fetched["vibe"]["vibe_score"], expected)


class TestUserVotesSignalWindow:
    """user_feedback_signal reads FeedbackLog in the last 120 minutes."""

    def test_five_dead_votes_drop_score_toward_zero(self, api, clean_venue):
        vid = clean_venue
        before = _get_venue(api, vid)["external_signals"]["user_votes_score"]
        # Baseline is 5.0 (neutral) with an empty feedback log.
        assert math.isclose(before, 5.0, abs_tol=0.5)

        for _ in range(5):
            r = api.post(
                f"{BASE_URL}/api/feedback",
                json={"venue_id": vid, "vote": "dead"},
                timeout=15,
            )
            assert r.status_code == 200

        after = _get_venue(api, vid)["external_signals"]["user_votes_score"]
        # 5 * -2 = -10 -> capped at -5 -> 5+(-5) = 0.0
        assert after < before
        assert after <= 0.0 + 0.01, after

    def test_five_busy_votes_climb_score_toward_ten(self, api, clean_venue):
        vid = clean_venue
        before = _get_venue(api, vid)["external_signals"]["user_votes_score"]
        assert math.isclose(before, 5.0, abs_tol=0.5)

        for _ in range(5):
            r = api.post(
                f"{BASE_URL}/api/feedback",
                json={"venue_id": vid, "vote": "busy"},
                timeout=15,
            )
            assert r.status_code == 200

        after = _get_venue(api, vid)["external_signals"]["user_votes_score"]
        # 5 * +2 = +10 -> capped at +5 -> 5+5 = 10.0
        assert after > before
        assert after >= 10.0 - 0.01, after
