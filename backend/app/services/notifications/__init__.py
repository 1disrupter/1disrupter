# -*- coding: utf-8 -*-
"""Push notifications — Expo push API wrapper + milestone triggers.

Fire-and-forget. Never raises into caller routes.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

import requests
from sqlalchemy.orm import Session

from app.models.push_token import UserPushToken

logger = logging.getLogger("vibe2nite.push")

EXPO_URL = "https://exp.host/--/api/v2/push/send"
MILESTONES = (10, 25, 50, 100)


def register_token(db: Session, *, wallet_id: str, expo_push_token: str) -> UserPushToken:
    from datetime import datetime, timezone
    row = db.get(UserPushToken, wallet_id)
    if row is None:
        row = UserPushToken(wallet_id=wallet_id, expo_push_token=expo_push_token)
        db.add(row)
    else:
        row.expo_push_token = expo_push_token
        row.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return row


def get_token(db: Session, wallet_id: str) -> Optional[str]:
    row = db.get(UserPushToken, wallet_id)
    return row.expo_push_token if row else None


def send_push(
    db: Session,
    *,
    wallet_id: str,
    title: str,
    body: str,
    data: Optional[dict[str, Any]] = None,
) -> dict:
    """Send a push to the wallet's registered Expo token. Returns a result dict.

    Safe on failure: logs and returns `{"ok": False, "error": ...}` — never raises.
    """
    token = get_token(db, wallet_id)
    if not token:
        return {"ok": False, "error": "no token registered"}

    payload = {
        "to": token,
        "title": title,
        "body": body,
        "sound": "default",
        "priority": "high",
        "channelId": "default",
    }
    if data:
        payload["data"] = data

    try:
        r = requests.post(
            EXPO_URL,
            json=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=6,
        )
        if not r.ok:
            logger.warning("expo push %s → %s", wallet_id, r.status_code)
            return {"ok": False, "error": f"expo http {r.status_code}", "response": r.text[:200]}
        return {"ok": True, "response": r.json()}
    except Exception as exc:  # pragma: no cover
        logger.exception("expo push failed: %s", exc)
        return {"ok": False, "error": str(exc)}


def milestone_for(previous: int, new: int) -> Optional[int]:
    """Return the first milestone crossed between previous and new credit totals, if any."""
    for m in MILESTONES:
        if previous < m <= new:
            return m
    return None


def send_milestone_push(db: Session, *, wallet_id: str, milestone: int, total: int) -> dict:
    return send_push(
        db,
        wallet_id=wallet_id,
        title=f"🎉 {milestone} Vibe Credits!",
        body=f"You just hit {total}. Redeem a drink or a free entry in the Wallet tab.",
        data={"type": "milestone", "milestone": milestone, "total": total},
    )
