# -*- coding: utf-8 -*-
"""Outbound webhook dispatcher.

Fire-and-forget POST to Slack/Discord-compatible webhook URLs. Configured
via env vars only — if a variable is empty the dispatcher is a no-op and
logs nothing at ERROR level.

Event types:
    VIBE_SPIKE      → WEBHOOK_VIBE_SPIKE_URL
    VENUE_CLAIMED   → WEBHOOK_VENUE_CLAIMED_URL
    VENUE_CLOSED    → WEBHOOK_VENUE_CLOSED_URL

Retry policy: one retry on network errors, 2s backoff.
"""
from __future__ import annotations

import logging
import os
import threading
import time
from typing import Any, Optional

import requests

logger = logging.getLogger("vibe2nite.webhooks")

# -- env → URL mapping (empty values are interpreted as "no webhook") --------
ENV_MAP = {
    "VIBE_SPIKE":    "WEBHOOK_VIBE_SPIKE_URL",
    "VENUE_CLAIMED": "WEBHOOK_VENUE_CLAIMED_URL",
    "VENUE_CLOSED":  "WEBHOOK_VENUE_CLOSED_URL",
}

# Recent dispatch log (in-memory ring, last 50) — kept as a hot cache on top
# of the durable `webhook_event_log` table so the admin "recent events" view
# is fast even under chatty dispatch patterns.
_RECENT: list[dict] = []
_MAX_RECENT = 50
_lock = threading.Lock()


def _persist_db(entry: dict, attempts: int) -> None:
    """Best-effort DB persistence — never raises into the dispatcher."""
    try:
        from app.core.database import SessionLocal
        from app.models.webhook_log import WebhookEventLog
        s = SessionLocal()
        try:
            row = WebhookEventLog(
                event_type=entry["event_type"],
                title=entry["title"],
                body=entry.get("body") or "",
                meta=entry.get("meta") or {},
                ok=bool(entry.get("ok")),
                error=(entry.get("error") or "")[:300],
                attempts=str(attempts),
            )
            s.add(row)
            s.commit()
        finally:
            s.close()
    except Exception as exc:  # pragma: no cover
        logger.debug("webhook DB persist failed: %s", exc)


def _record(entry: dict, attempts: int = 1) -> None:
    with _lock:
        _RECENT.append(entry)
        if len(_RECENT) > _MAX_RECENT:
            del _RECENT[: len(_RECENT) - _MAX_RECENT]
    _persist_db(entry, attempts)


def recent_events(limit: int = 20) -> list[dict]:
    """Return the last N events — DB first (durable), fallback to in-memory."""
    try:
        from app.core.database import SessionLocal
        from app.models.webhook_log import WebhookEventLog
        s = SessionLocal()
        try:
            rows = (
                s.query(WebhookEventLog)
                .order_by(WebhookEventLog.created_at.desc())
                .limit(limit)
                .all()
            )
            return [r.as_dict() for r in rows]
        finally:
            s.close()
    except Exception:  # pragma: no cover
        with _lock:
            return list(_RECENT[-limit:][::-1])


def is_configured(event_type: str) -> bool:
    env_name = ENV_MAP.get(event_type)
    if not env_name:
        return False
    return bool(os.environ.get(env_name, "").strip())


def _build_slack_payload(event_type: str, title: str, body: str, meta: dict) -> dict:
    """Slack + Discord both accept `{"text": "..."}`; we also send full fields
    for Slack Block Kit and Discord's `embeds` consumers that inspect them."""
    color = {
        "VIBE_SPIKE":    "#B15CFF",
        "VENUE_CLAIMED": "#FF2EC4",
        "VENUE_CLOSED":  "#6B6B6B",
    }.get(event_type, "#00F5FF")
    plain = f"*[{event_type}]* {title}\n{body}"
    if meta:
        plain += "\n" + "\n".join(f"• _{k}_: `{v}`" for k, v in meta.items())
    return {
        "text": plain,
        "attachments": [
            {
                "color": color,
                "title": f"Vibe2Nite · {event_type}",
                "text": f"*{title}*\n{body}",
                "fields": [{"title": k, "value": str(v), "short": True} for k, v in (meta or {}).items()],
            }
        ],
        # Discord-friendly embeds (webhook URL is the same contract)
        "embeds": [
            {
                "title": f"{event_type} · {title}",
                "description": body,
                "color": int(color.lstrip("#"), 16),
                "fields": [{"name": k, "value": str(v), "inline": True} for k, v in (meta or {}).items()],
            }
        ],
    }


def _post(url: str, payload: dict, attempt: int = 1) -> tuple[bool, Optional[str]]:
    try:
        r = requests.post(url, json=payload, timeout=4)
        if 200 <= r.status_code < 300:
            return True, None
        return False, f"http_{r.status_code}"
    except Exception as exc:  # pragma: no cover
        return False, str(exc)[:160]


def _dispatch_sync(event_type: str, title: str, body: str, meta: dict) -> None:
    url = os.environ.get(ENV_MAP.get(event_type, ""), "").strip()
    if not url:
        return
    payload = _build_slack_payload(event_type, title, body, meta)
    ok, err = _post(url, payload)
    attempts = 1
    if not ok:
        time.sleep(2)
        ok, err = _post(url, payload, attempt=2)
        attempts = 2
    entry = {
        "event_type": event_type,
        "title": title,
        "body": body,
        "ok": ok,
        "error": err,
        "ts": time.time(),
        "meta": meta,
    }
    _record(entry, attempts=attempts)
    if ok:
        logger.info("webhook dispatched event=%s title=%s", event_type, title)
    else:
        logger.warning("webhook failed event=%s err=%s", event_type, err)


def dispatch(event_type: str, *, title: str, body: str, meta: Optional[dict] = None) -> None:
    """Fire-and-forget. Never blocks the caller, never raises."""
    if event_type not in ENV_MAP:
        logger.debug("unknown webhook event_type=%s", event_type)
        return
    meta = meta or {}
    # Run in a daemon thread so the main request/job returns immediately.
    t = threading.Thread(
        target=_dispatch_sync,
        args=(event_type, title, body, meta),
        daemon=True,
        name=f"webhook-{event_type}",
    )
    t.start()
