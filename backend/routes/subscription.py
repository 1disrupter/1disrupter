"""
AlphaAI Subscription Status Routes
Endpoint for frontend to check current subscription state.
"""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request

logger = logging.getLogger("AlphaAI.Subscription")

router = APIRouter(prefix="/api", tags=["subscription"])

db = None

def init_db(database):
    global db
    db = database


@router.get("/subscription/status")
async def get_subscription_status(request: Request):
    """
    Get current subscription status for the authenticated user.
    Returns tier, status, period_end, and feature flags.
    """
    # Check for demo
    demo = request.query_params.get("demo", "false").lower() == "true"
    if demo:
        return {
            "success": True,
            "subscription": {
                "status": "active",
                "tier": "pro",
                "is_pro": True,
                "period_end": None,
                "cancel_at_period_end": False,
            },
            "demo": True,
        }

    # Check for wallet-based lookup
    wallet = request.query_params.get("wallet_address")
    if wallet and wallet != "demo_user":
        investor = await db.investors.find_one({"wallet_address": wallet}, {"_id": 0})
        if investor:
            return {
                "success": True,
                "subscription": {
                    "status": "active" if investor.get("is_pro") else "inactive",
                    "tier": "elite" if investor.get("is_elite") else ("pro" if investor.get("is_pro") else "free"),
                    "is_pro": investor.get("is_pro", False),
                    "period_end": None,
                    "cancel_at_period_end": False,
                    "pro_since": investor.get("pro_since"),
                },
            }

    # Token-based lookup
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        from routes.auth import decode_token, get_user_by_id
        payload = decode_token(auth_header.split(" ")[1])
        if not payload or payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await get_user_by_id(payload.get("sub"))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")

    tier = user.get("user_tier", "free")
    sub_status = user.get("subscription_status", "active" if tier in ("pro", "elite") else "inactive")
    period_end = user.get("subscription_end")

    return {
        "success": True,
        "subscription": {
            "status": sub_status,
            "tier": tier,
            "is_pro": tier in ("pro", "elite"),
            "period_end": period_end.isoformat() if isinstance(period_end, datetime) else period_end,
            "cancel_at_period_end": user.get("cancel_at_period_end", False),
            "pro_since": user.get("pro_since"),
            "stripe_customer_id": user.get("stripe_customer_id"),
        },
    }


@router.get("/subscription/webhook-events")
async def get_webhook_events(request: Request, limit: int = 20):
    """Admin endpoint to view recent webhook events (for testing/debugging)."""
    admin_key = request.query_params.get("admin_key", "")
    import os
    if admin_key != os.environ.get("ADMIN_SECRET"):
        raise HTTPException(status_code=403, detail="Admin access denied")

    events = await db.stripe_webhook_events.find(
        {}, {"_id": 0}
    ).sort("processed_at", -1).to_list(limit)

    return {
        "success": True,
        "events": events,
        "count": len(events),
    }
