# -*- coding: utf-8 -*-
"""Weighted Vibe Score + crowd level logic."""
from app.models.vibe import CrowdLevel, Vibe

# Weights (must sum to 1.0)
WEIGHTS = {
    "manual_score": 0.25,
    "social_activity": 0.25,
    "user_votes": 0.25,
    "time_prediction": 0.15,
    "venue_boost": 0.10,
}

# Vote → delta applied to the `user_votes` signal
VOTE_DELTAS = {"busy": 1.0, "good": 0.5, "dead": -1.0}


def compute_vibe_score(signals: dict) -> float:
    """Weighted sum of signals, capped at 10, floored at 0."""
    raw = sum(float(signals.get(k, 0.0)) * w for k, w in WEIGHTS.items())
    return round(min(max(raw, 0.0), 10.0), 2)


def crowd_level_from_score(score: float) -> CrowdLevel:
    if score >= 8:
        return CrowdLevel.busy
    if score >= 5:
        return CrowdLevel.medium
    return CrowdLevel.dead


def recompute_from_vibe(vibe: Vibe) -> tuple[float, CrowdLevel]:
    """Convenience: recompute score & crowd directly from an ORM Vibe instance."""
    score = compute_vibe_score(vibe.signals_dict())
    return score, crowd_level_from_score(score)


# ---------------------------------------------------------------------------
# Signal-Engine aware variant (added; does NOT replace compute_vibe_score)
# ---------------------------------------------------------------------------
def calculate_vibe_score_from_signals(signals, manual_score: float, venue_boost: float) -> float:
    """Weighted blend using the cached VenueSignals row + manual inputs.

    Formula (requested):
        score = manual_score*0.25 + signals.social_score*0.25
              + signals.user_votes_score*0.25 + signals.time_score*0.15
              + venue_boost*0.10
    Clamped to [0, 10]. Accepts either a VenueSignals ORM row or a dict
    with the same keys — makes testing painless.
    """
    def _g(k: str) -> float:
        return float(getattr(signals, k, None) if not isinstance(signals, dict) else signals.get(k, 0.0) or 0.0)

    raw = (
        float(manual_score or 0.0) * 0.25
        + _g("social_score") * 0.25
        + _g("user_votes_score") * 0.25
        + _g("time_score") * 0.15
        + float(venue_boost or 0.0) * 0.10
    )
    return round(min(max(raw, 0.0), 10.0), 2)
