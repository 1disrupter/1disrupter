# -*- coding: utf-8 -*-
"""Reward rules — central source of truth for "how many credits does X give".

Keep additive. New rules can be added without breaking existing clients.
"""
from __future__ import annotations

from typing import Dict

# Canonical rule map.
REWARD_RULES: Dict[str, int] = {
    "feedback": 1,          # user submitted a busy/good/dead vote
    "visit": 3,             # a real dwell-time visit was detected
    "navigate": 1,          # user hit "Go" / opened directions
    "daily_login": 1,       # one-a-day login ping
    "first_visit_bonus": 5, # first time visiting a venue (client-computed)
    "referral": 5,          # someone you invited took their first credit-eligible action
}


def credits_for(action: str) -> int:
    return int(REWARD_RULES.get(action, 0))


def list_rules() -> dict:
    return dict(REWARD_RULES)
