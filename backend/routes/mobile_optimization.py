"""
AlphaAI Mobile Bootstrap & Optimization Endpoints
Lightweight endpoints for fast mobile web initialization and token refresh.
"""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException

logger = logging.getLogger("AlphaAI.MobileOpt")

router = APIRouter(prefix="/api/mobile", tags=["mobile-optimization"])

db = None

def init_db(database):
    global db
    db = database


DEMO_BOOTSTRAP = {
    "user": {
        "id": "demo-user",
        "name": "Demo Trader",
        "email": "demo@alphaai.com",
        "user_tier": "pro",
        "is_pro": True,
    },
    "followed_strategies": [
        {"id": "demo-1", "name": "BTC Momentum Alpha", "asset": "BTC/USDT"},
        {"id": "demo-2", "name": "ETH Mean Reversion", "asset": "ETH/USDT"},
        {"id": "demo-3", "name": "SOL Breakout Trader", "asset": "SOL/USDT"},
    ],
    "unread_alerts": 3,
    "feature_flags": {
        "demo_mode": True,
        "mobile_optimized": True,
        "real_time_alerts": True,
        "strategy_lab": True,
    },
    "strategies_summary": {
        "total": 12,
        "top_performer": {"name": "BTC Momentum Alpha", "sharpe": 2.41},
    },
}


# ── GET /api/mobile/bootstrap ───────────────────────────────────

@router.get("/bootstrap")
async def mobile_bootstrap(request: Request):
    """
    Lightweight endpoint for fast mobile initialization.
    Returns user profile, followed strategies, unread alerts, and feature flags.
    Target: <50ms.
    """
    # Check for demo mode
    demo = request.query_params.get("demo", "false").lower() == "true"
    if demo:
        return {**DEMO_BOOTSTRAP, "timestamp": datetime.now(timezone.utc).isoformat()}

    # Authenticated user
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

    user_id = user["id"]

    # Parallel lightweight queries
    followed = await db.followed_strategies.find(
        {"user_id": user_id}, {"_id": 0, "strategy_id": 1}
    ).to_list(50)
    followed_ids = [f["strategy_id"] for f in followed]

    # Fetch minimal strategy metadata for followed strategies
    followed_strategies = []
    if followed_ids:
        strats = await db.strategy_leaderboard.find(
            {"id": {"$in": followed_ids}},
            {"_id": 0, "id": 1, "name": 1, "asset": 1},
        ).to_list(50)
        followed_strategies = strats

    unread = await db.notifications_inbox.count_documents(
        {"user_id": user_id, "read": False}
    )

    # Top strategy summary
    top = await db.strategy_leaderboard.find_one(
        {}, {"_id": 0, "name": 1, "metrics.sharpe_ratio": 1},
        sort=[("metrics.sharpe_ratio", -1)],
    )
    total_strats = await db.strategy_leaderboard.count_documents({})

    return {
        "user": {
            "id": user["id"],
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "user_tier": user.get("user_tier", "free"),
            "is_pro": user.get("user_tier") in ("pro", "elite"),
            "subscription_status": user.get("subscription_status", "active" if user.get("user_tier") in ("pro", "elite") else "inactive"),
            "subscription_end": user.get("subscription_end").isoformat() if user.get("subscription_end") else None,
        },
        "followed_strategies": followed_strategies,
        "unread_alerts": unread,
        "feature_flags": {
            "demo_mode": False,
            "mobile_optimized": True,
            "real_time_alerts": user.get("user_tier") in ("pro", "elite"),
            "strategy_lab": True,
        },
        "strategies_summary": {
            "total": total_strats,
            "top_performer": {
                "name": top.get("name", "N/A") if top else "N/A",
                "sharpe": top.get("metrics", {}).get("sharpe_ratio", 0) if top else 0,
            },
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ── POST /api/mobile/refresh ───────────────────────────────────

@router.post("/refresh")
async def mobile_refresh(request: Request):
    """
    Lightweight token refresh optimized for mobile.
    Minimal payload, fast response.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    refresh_token = body.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="refresh_token required")

    from routes.auth import decode_token, get_user_by_id, create_access_token

    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = await get_user_by_id(payload.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access = create_access_token({"sub": user["id"]})

    return {
        "access_token": new_access,
        "token_type": "bearer",
        "user_tier": user.get("user_tier", "free"),
    }
