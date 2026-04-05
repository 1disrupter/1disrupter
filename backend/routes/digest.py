"""
Weekly Digest Routes — Unsubscribe + Admin Analytics + Manual Trigger.
"""
import os
import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Query

from database import db

logger = logging.getLogger("AlphaAI.DigestRoutes")
router = APIRouter(prefix="/api/digest", tags=["Weekly Digest"])

digest_logs_col = db["weekly_digest_logs"]
digest_prefs_col = db["digest_preferences"]

ADMIN_SECRET = os.environ.get("ADMIN_SECRET")


# ═══════════════════════════════════════════
#  UNSUBSCRIBE
# ═══════════════════════════════════════════

@router.get("/unsubscribe")
async def unsubscribe_digest(email: str = Query(...)):
    """Unsubscribe a user from weekly digest emails."""
    email_clean = email.lower().strip()
    now = datetime.now(timezone.utc).isoformat()

    await digest_prefs_col.update_one(
        {"email": email_clean},
        {"$set": {"email": email_clean, "unsubscribed": True, "updated_at": now}},
        upsert=True,
    )

    logger.info(f"Digest unsubscribe: {email_clean}")
    return {"message": "You have been unsubscribed from the weekly digest."}


@router.get("/resubscribe")
async def resubscribe_digest(email: str = Query(...)):
    """Re-subscribe a user to weekly digest emails."""
    email_clean = email.lower().strip()
    now = datetime.now(timezone.utc).isoformat()

    await digest_prefs_col.update_one(
        {"email": email_clean},
        {"$set": {"unsubscribed": False, "updated_at": now}},
    )

    return {"message": "You have been re-subscribed to the weekly digest."}


# ═══════════════════════════════════════════
#  ADMIN ANALYTICS
# ═══════════════════════════════════════════

@router.get("/admin/analytics")
async def digest_analytics(admin_key: str = Query(...)):
    """Admin: Weekly digest delivery analytics."""
    if admin_key != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Admin access denied")

    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).isoformat()

    total_sent = await digest_logs_col.count_documents({})
    sent_last_7d = await digest_logs_col.count_documents({"sent_at": {"$gte": week_ago}})
    errors_last_7d = await digest_logs_col.count_documents({"sent_at": {"$gte": week_ago}, "status": "error"})

    # Pro vs Free distribution (last 7 days)
    pro_sent = await digest_logs_col.count_documents({"sent_at": {"$gte": week_ago}, "is_pro": True})
    free_sent = await digest_logs_col.count_documents({"sent_at": {"$gte": week_ago}, "is_pro": False})

    # Unsubscribed count
    unsubscribed = await digest_prefs_col.count_documents({"unsubscribed": True})

    # Most recent batch
    latest_log = await digest_logs_col.find_one(
        {}, {"_id": 0, "sent_at": 1, "week_label": 1},
        sort=[("sent_at", -1)]
    )

    return {
        "total_digests_sent": total_sent,
        "last_7d": {
            "sent": sent_last_7d,
            "errors": errors_last_7d,
            "delivery_rate": round((sent_last_7d - errors_last_7d) / sent_last_7d * 100, 1) if sent_last_7d > 0 else 0,
        },
        "pro_vs_free": {
            "pro": pro_sent,
            "free": free_sent,
        },
        "unsubscribed_total": unsubscribed,
        "latest_batch": {
            "sent_at": latest_log.get("sent_at") if latest_log else None,
            "week_label": latest_log.get("week_label") if latest_log else None,
        },
        "open_rate": None,  # Placeholder — requires tracking pixel or Resend webhooks
    }


# ═══════════════════════════════════════════
#  MANUAL TRIGGER (Admin)
# ═══════════════════════════════════════════

@router.post("/admin/trigger")
async def trigger_digest(admin_key: str = Query(...)):
    """Admin: Manually trigger a weekly digest send."""
    if admin_key != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Admin access denied")

    from cron.weekly_digest import run_weekly_digest
    result = await run_weekly_digest()

    return {"message": "Weekly digest triggered", "result": result}
