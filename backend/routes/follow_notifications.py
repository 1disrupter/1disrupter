"""
AlphaAI Follow Strategy + In-App Notifications + Pro Gating
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime, timezone
import uuid
from database import db, logger
from routes.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Follow & Notifications"])

FREE_FOLLOW_LIMIT = 1

# ── Helpers ────────────────────────────────────────────────────

def is_pro(user: dict) -> bool:
    tier = user.get("user_tier", "free")
    if tier in ("pro", "elite"):
        return True
    return user.get("is_pro", False) or user.get("is_elite", False)


# ── Follow Strategy ────────────────────────────────────────────

@router.post("/strategies/{strategy_id}/follow")
async def follow_strategy(strategy_id: str, user: dict = Depends(get_current_user)):
    user_id = user["id"]

    existing = await db.followed_strategies.find_one({"user_id": user_id, "strategy_id": strategy_id})
    if existing:
        return {"success": True, "message": "Already following", "following": True}

    if not is_pro(user):
        count = await db.followed_strategies.count_documents({"user_id": user_id})
        if count >= FREE_FOLLOW_LIMIT:
            raise HTTPException(
                status_code=403,
                detail=f"Free tier limited to {FREE_FOLLOW_LIMIT} follow. Upgrade to Pro for unlimited follows."
            )

    await db.followed_strategies.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "strategy_id": strategy_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    # Create a welcome notification
    await _create_notification(
        user_id=user_id,
        strategy_id=strategy_id,
        message=f"You are now following strategy {strategy_id[:8]}... — you'll receive signal updates.",
        notif_type="follow",
    )
    return {"success": True, "message": "Strategy followed", "following": True}


@router.post("/strategies/{strategy_id}/unfollow")
async def unfollow_strategy(strategy_id: str, user: dict = Depends(get_current_user)):
    result = await db.followed_strategies.delete_one({"user_id": user["id"], "strategy_id": strategy_id})
    return {"success": True, "message": "Unfollowed" if result.deleted_count else "Not following", "following": False}


@router.get("/strategies/following")
async def get_following(user: dict = Depends(get_current_user)):
    entries = await db.followed_strategies.find(
        {"user_id": user["id"]}, {"_id": 0}
    ).sort("created_at", -1).to_list(100)

    strategy_ids = [e["strategy_id"] for e in entries]

    # Enrich with strategy data
    strategies = []
    if strategy_ids:
        for sid in strategy_ids:
            strat = await db.strategy_leaderboard.find_one({"id": sid}, {"_id": 0})
            if strat:
                strat["followed_at"] = next((e["created_at"] for e in entries if e["strategy_id"] == sid), None)
                strategies.append(strat)

    return {"success": True, "following": strategies, "count": len(strategies), "is_pro": is_pro(user)}


@router.get("/strategies/following/ids")
async def get_following_ids(user: dict = Depends(get_current_user)):
    entries = await db.followed_strategies.find(
        {"user_id": user["id"]}, {"_id": 0, "strategy_id": 1}
    ).to_list(500)
    return {"ids": [e["strategy_id"] for e in entries]}


# ── Demo Follow (no auth required) ────────────────────────────

DEMO_FOLLOWING = [
    {"id": "demo-1", "name": "BTC Momentum Alpha", "type": "momentum", "asset": "BTC/USDT", "metrics": {"sharpe_ratio": 2.14, "total_return": 24.8, "max_drawdown": 5.2, "win_rate": 68.5}, "data_source": "mock", "followed_at": "2026-03-28T12:00:00Z"},
    {"id": "demo-2", "name": "ETH Mean Reversion", "type": "mean_reversion", "asset": "ETH/USDT", "metrics": {"sharpe_ratio": 1.87, "total_return": 18.3, "max_drawdown": 4.1, "win_rate": 62.3}, "data_source": "mock", "followed_at": "2026-03-27T10:00:00Z"},
]

@router.get("/strategies/following/demo")
async def get_demo_following():
    return {"success": True, "following": DEMO_FOLLOWING, "count": len(DEMO_FOLLOWING), "is_pro": True}


# ── In-App Notifications ──────────────────────────────────────

async def _create_notification(user_id: str, strategy_id: str, message: str, notif_type: str = "signal"):
    doc = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "strategy_id": strategy_id,
        "message": message,
        "type": notif_type,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.notifications_inbox.insert_one(doc)
    return doc


async def notify_followers(strategy_id: str, message: str, notif_type: str = "signal"):
    """Called when a strategy generates a signal — notifies all followers and broadcasts via WebSocket."""
    from services.alerts_manager import alerts_manager

    followers = await db.followed_strategies.find(
        {"strategy_id": strategy_id}, {"_id": 0, "user_id": 1}
    ).to_list(1000)

    user_ids = []
    for f in followers:
        await _create_notification(f["user_id"], strategy_id, message, notif_type)
        user_ids.append(f["user_id"])

    # Broadcast to connected WebSocket clients
    if user_ids:
        ws_payload = {
            "type": "strategy_alert",
            "strategy_id": strategy_id,
            "message": message,
            "notif_type": notif_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await alerts_manager.broadcast_to_users(user_ids, ws_payload)

    return len(followers)


@router.get("/notifications/inbox")
async def get_notifications(
    user: dict = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
):
    query = {"user_id": user["id"]}
    if unread_only:
        query["read"] = False
    items = await db.notifications_inbox.find(
        query, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)

    unread = await db.notifications_inbox.count_documents({"user_id": user["id"], "read": False})
    return {"success": True, "notifications": items, "unread_count": unread}


@router.post("/notifications/{notif_id}/read")
async def mark_notification_read(notif_id: str, user: dict = Depends(get_current_user)):
    await db.notifications_inbox.update_one(
        {"id": notif_id, "user_id": user["id"]},
        {"$set": {"read": True}}
    )
    return {"success": True}


@router.post("/notifications/read-all")
async def mark_all_read(user: dict = Depends(get_current_user)):
    result = await db.notifications_inbox.update_many(
        {"user_id": user["id"], "read": False},
        {"$set": {"read": True}}
    )
    return {"success": True, "marked": result.modified_count}


# ── Demo Notifications ─────────────────────────────────────────

DEMO_NOTIFICATIONS = [
    {"id": "dn-1", "strategy_id": "demo-1", "message": "BTC Momentum Alpha triggered LONG signal at $67,250 (confidence: 84%)", "type": "signal", "read": False, "created_at": "2026-03-29T09:42:00Z"},
    {"id": "dn-2", "strategy_id": "demo-2", "message": "ETH Mean Reversion closed position — PnL: +$342 (+2.1%)", "type": "signal", "read": False, "created_at": "2026-03-29T08:15:00Z"},
    {"id": "dn-3", "strategy_id": "demo-1", "message": "BTC Momentum Alpha hit take-profit target — total P&L: +$1,240", "type": "signal", "read": True, "created_at": "2026-03-28T22:30:00Z"},
    {"id": "dn-4", "strategy_id": "demo-2", "message": "You are now following ETH Mean Reversion", "type": "follow", "read": True, "created_at": "2026-03-27T10:00:00Z"},
]

@router.get("/notifications/inbox/demo")
async def get_demo_notifications():
    unread = sum(1 for n in DEMO_NOTIFICATIONS if not n["read"])
    return {"success": True, "notifications": DEMO_NOTIFICATIONS, "unread_count": unread}


# ── Pro Gating Check ────────────────────────────────────────────

@router.get("/user/pro-status")
async def check_pro_status(user: dict = Depends(get_current_user)):
    return {
        "is_pro": is_pro(user),
        "tier": user.get("user_tier", "free"),
        "follow_limit": None if is_pro(user) else FREE_FOLLOW_LIMIT,
    }
