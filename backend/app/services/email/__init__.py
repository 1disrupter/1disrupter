# -*- coding: utf-8 -*-
"""Resend email client — thin async wrapper.

When RESEND_API_KEY is empty the client degrades gracefully: it logs the
rendered email to stdout and returns {'sent': False, 'console_only': True}
so calling code can still surface the magic-link URL to the admin.
"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional

logger = logging.getLogger("vibe2nite.email")


def is_configured() -> bool:
    return bool(os.environ.get("RESEND_API_KEY", "").strip())


async def send_email(
    *, to: str, subject: str, html: str, text: Optional[str] = None,
) -> dict:
    """Send a transactional email. Returns a small status dict."""
    api_key = os.environ.get("RESEND_API_KEY", "").strip()
    sender  = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev").strip() or "onboarding@resend.dev"

    if not api_key:
        logger.info(
            "EMAIL (console-only, no RESEND_API_KEY) → to=%s subject=%r\n%s",
            to, subject, (text or html),
        )
        return {"sent": False, "console_only": True, "to": to}

    try:
        import resend
        resend.api_key = api_key
        params = {
            "from": sender,
            "to": [to],
            "subject": subject,
            "html": html,
        }
        if text:
            params["text"] = text
        # Resend SDK is synchronous — run it in a thread to stay non-blocking.
        res = await asyncio.to_thread(resend.Emails.send, params)
        email_id = res.get("id") if isinstance(res, dict) else getattr(res, "id", None)
        logger.info("email sent id=%s to=%s subject=%r", email_id, to, subject)
        return {"sent": True, "id": email_id, "to": to}
    except Exception as exc:  # pragma: no cover
        logger.exception("resend email failed to=%s: %s", to, exc)
        return {"sent": False, "error": str(exc)[:200], "to": to}
