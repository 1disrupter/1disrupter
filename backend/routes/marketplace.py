"""
Strategy Marketplace Module
New standalone marketplace backend — does NOT touch existing Strategy Lab logic.
Collections: strategies_mp, strategy_performance, strategy_signals,
             strategy_subscriptions, strategy_reviews, creator_payouts, automation_webhooks
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId
import uuid
import logging

from database import db
from routes.auth import get_current_user

logger = logging.getLogger("AlphaAI.Marketplace")
router = APIRouter(prefix="/api/marketplace", tags=["Marketplace"])

# ─── Collections (initialised at import, motor is lazy) ───
strategies_col = db["strategies_mp"]
performance_col = db["strategy_performance"]
signals_col = db["strategy_signals"]
subscriptions_col = db["strategy_subscriptions"]
reviews_col = db["strategy_reviews"]
payouts_col = db["creator_payouts"]
webhooks_col = db["automation_webhooks"]

VALID_CATEGORIES = {"trend", "scalping", "btc", "eth", "sol", "xrp", "momentum", "mean_reversion", "arbitrage", "other"}
VALID_STATUSES = {"draft", "published", "disabled"}


# ═══════════════════════════════════════════
#  Pydantic Schemas
# ═══════════════════════════════════════════

class StrategyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str = Field("", max_length=2000)
    category: str = Field("other")
    parameters: dict = Field(default_factory=dict)
    is_public: bool = Field(False)

class StrategyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = None
    parameters: Optional[dict] = None

class PerformanceUpload(BaseModel):
    sharpe_ratio: Optional[float] = None
    win_rate: Optional[float] = None
    max_drawdown: Optional[float] = None
    total_return: Optional[float] = None
    total_trades: Optional[int] = None
    avg_trade_pnl: Optional[float] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    extra: dict = Field(default_factory=dict)

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field("", max_length=1000)


# ═══════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════

def _sanitize(doc: dict) -> dict:
    """Remove _id and any ObjectId fields for JSON safety."""
    doc.pop("_id", None)
    return doc


async def _get_strategy_or_404(strategy_id: str) -> dict:
    strategy = await strategies_col.find_one({"id": strategy_id}, {"_id": 0})
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


async def _assert_owner(strategy: dict, user_id: str):
    if strategy["creator_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not the owner of this strategy")


# ═══════════════════════════════════════════
#  STRATEGIES CRUD
# ═══════════════════════════════════════════

@router.post("/strategies/create")
async def create_strategy(body: StrategyCreate, user: dict = Depends(get_current_user)):
    """Create a new strategy in draft mode."""
    cat = body.category.lower().strip()
    if cat and cat not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category. Choose from: {', '.join(sorted(VALID_CATEGORIES))}")

    now = datetime.now(timezone.utc).isoformat()
    strategy = {
        "id": str(uuid.uuid4()),
        "creator_id": user["id"],
        "creator_name": user.get("name", "Unknown"),
        "name": body.name.strip(),
        "description": body.description.strip(),
        "category": cat or "other",
        "parameters": body.parameters,
        "created_at": now,
        "updated_at": now,
        "is_public": body.is_public,
        "status": "draft",
        "subscriber_count": 0,
        "avg_rating": 0.0,
        "review_count": 0,
    }
    await strategies_col.insert_one(strategy)
    return _sanitize(strategy)


@router.post("/strategies/{strategy_id}/publish")
async def publish_strategy(strategy_id: str, user: dict = Depends(get_current_user)):
    """Publish a strategy to the marketplace."""
    strategy = await _get_strategy_or_404(strategy_id)
    await _assert_owner(strategy, user["id"])

    if strategy["status"] == "published":
        raise HTTPException(status_code=400, detail="Strategy is already published")

    await strategies_col.update_one(
        {"id": strategy_id},
        {"$set": {"status": "published", "is_public": True, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"message": "Strategy published", "id": strategy_id, "status": "published"}


@router.post("/strategies/{strategy_id}/unpublish")
async def unpublish_strategy(strategy_id: str, user: dict = Depends(get_current_user)):
    """Remove a strategy from the marketplace but keep data."""
    strategy = await _get_strategy_or_404(strategy_id)
    await _assert_owner(strategy, user["id"])

    if strategy["status"] != "published":
        raise HTTPException(status_code=400, detail="Strategy is not currently published")

    await strategies_col.update_one(
        {"id": strategy_id},
        {"$set": {"status": "draft", "is_public": False, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"message": "Strategy unpublished", "id": strategy_id, "status": "draft"}


@router.get("/strategies")
async def list_strategies(
    category: Optional[str] = Query(None, description="Filter by category"),
    creator: Optional[str] = Query(None, description="Filter by creator_id"),
    sort_by: str = Query("popularity", description="Sort: popularity | performance | newest | rating"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Marketplace listing with filters. Only shows published strategies."""
    query = {"status": "published", "is_public": True}

    if category:
        query["category"] = category.lower().strip()
    if creator:
        query["creator_id"] = creator

    sort_map = {
        "popularity": [("subscriber_count", -1)],
        "performance": [("avg_rating", -1)],
        "newest": [("created_at", -1)],
        "rating": [("avg_rating", -1), ("review_count", -1)],
    }
    sort_order = sort_map.get(sort_by, sort_map["popularity"])

    skip = (page - 1) * limit
    total = await strategies_col.count_documents(query)
    cursor = strategies_col.find(query, {"_id": 0}).sort(sort_order).skip(skip).limit(limit)
    items = await cursor.to_list(length=limit)

    return {
        "strategies": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit if total else 0,
    }


# ═══════════════════════════════════════════
#  STRATEGY LEADERBOARD (public, sorted, cached)
# ═══════════════════════════════════════════

_leaderboard_cache = {"data": None, "ts": 0}
LEADERBOARD_TTL = 60  # seconds

@router.get("/strategies/leaderboard")
async def strategy_leaderboard(
    sort_by: str = Query("total_return", description="Sort: total_return, sharpe_ratio, win_rate, max_drawdown"),
    order: str = Query("desc", description="asc or desc"),
):
    """Public strategy leaderboard with performance metrics. Cached for 60s."""
    import time
    now = time.time()

    # Check cache
    if _leaderboard_cache["data"] and (now - _leaderboard_cache["ts"]) < LEADERBOARD_TTL:
        cached = _leaderboard_cache["data"]
    else:
        query = {"status": "published", "is_public": True}
        cursor = strategies_col.find(query, {"_id": 0})
        items = await cursor.to_list(length=200)

        # Enrich with latest performance
        for s in items:
            perf = await performance_col.find_one(
                {"strategy_id": s["id"]}, {"_id": 0}, sort=[("uploaded_at", -1)]
            )
            s["_perf"] = perf or {}

        cached = items
        _leaderboard_cache["data"] = cached
        _leaderboard_cache["ts"] = now

    # Sort
    valid_sort = {"total_return", "sharpe_ratio", "win_rate", "max_drawdown"}
    sort_field = sort_by if sort_by in valid_sort else "total_return"
    reverse = order != "asc"

    sorted_items = sorted(
        cached,
        key=lambda s: s.get("_perf", {}).get(sort_field) or 0,
        reverse=reverse,
    )

    return {"strategies": sorted_items, "total": len(sorted_items)}


@router.get("/strategies/{strategy_id}")
async def get_strategy_detail(strategy_id: str):
    """Full strategy details including performance, recent signals, and reviews."""
    strategy = await _get_strategy_or_404(strategy_id)

    # Fetch latest performance record
    perf = await performance_col.find_one(
        {"strategy_id": strategy_id}, {"_id": 0}, sort=[("uploaded_at", -1)]
    )

    # Fetch last 20 signals
    signals_cursor = signals_col.find(
        {"strategy_id": strategy_id}, {"_id": 0}
    ).sort("created_at", -1).limit(20)
    signals = await signals_cursor.to_list(length=20)

    # Fetch last 10 reviews
    reviews_cursor = reviews_col.find(
        {"strategy_id": strategy_id}, {"_id": 0}
    ).sort("created_at", -1).limit(10)
    reviews = await reviews_cursor.to_list(length=10)

    return {
        "strategy": strategy,
        "performance": perf,
        "signals": signals,
        "reviews": reviews,
    }


# ═══════════════════════════════════════════
#  PERFORMANCE
# ═══════════════════════════════════════════

@router.post("/strategies/{strategy_id}/performance")
async def upload_performance(strategy_id: str, body: PerformanceUpload, user: dict = Depends(get_current_user)):
    """Upload performance data for a strategy (creator only)."""
    strategy = await _get_strategy_or_404(strategy_id)
    await _assert_owner(strategy, user["id"])

    now = datetime.now(timezone.utc).isoformat()
    record = {
        "id": str(uuid.uuid4()),
        "strategy_id": strategy_id,
        "sharpe_ratio": body.sharpe_ratio,
        "win_rate": body.win_rate,
        "max_drawdown": body.max_drawdown,
        "total_return": body.total_return,
        "total_trades": body.total_trades,
        "avg_trade_pnl": body.avg_trade_pnl,
        "period_start": body.period_start,
        "period_end": body.period_end,
        "extra": body.extra,
        "uploaded_at": now,
    }
    await performance_col.insert_one(record)
    return _sanitize(record)


# ═══════════════════════════════════════════
#  SUBSCRIPTIONS
# ═══════════════════════════════════════════

@router.post("/strategies/{strategy_id}/subscribe")
async def subscribe_to_strategy(strategy_id: str, user: dict = Depends(get_current_user)):
    """Subscribe to a strategy. Creates DB entry (Stripe integration placeholder)."""
    strategy = await _get_strategy_or_404(strategy_id)

    if strategy["status"] != "published":
        raise HTTPException(status_code=400, detail="Cannot subscribe to an unpublished strategy")

    if strategy["creator_id"] == user["id"]:
        raise HTTPException(status_code=400, detail="Cannot subscribe to your own strategy")

    existing = await subscriptions_col.find_one(
        {"strategy_id": strategy_id, "user_id": user["id"], "status": "active"}
    )
    if existing:
        raise HTTPException(status_code=409, detail="Already subscribed to this strategy")

    now = datetime.now(timezone.utc).isoformat()
    sub = {
        "id": str(uuid.uuid4()),
        "strategy_id": strategy_id,
        "strategy_name": strategy["name"],
        "user_id": user["id"],
        "user_email": user.get("email", ""),
        "creator_id": strategy["creator_id"],
        "status": "active",
        "stripe_subscription_id": None,
        "subscribed_at": now,
        "canceled_at": None,
    }
    await subscriptions_col.insert_one(sub)

    # Increment subscriber count
    await strategies_col.update_one(
        {"id": strategy_id}, {"$inc": {"subscriber_count": 1}}
    )

    return {"message": "Subscribed successfully", "subscription": _sanitize(sub)}


@router.post("/strategies/{strategy_id}/unsubscribe")
async def unsubscribe_from_strategy(strategy_id: str, user: dict = Depends(get_current_user)):
    """Unsubscribe from a strategy."""
    sub = await subscriptions_col.find_one(
        {"strategy_id": strategy_id, "user_id": user["id"], "status": "active"}
    )
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription found")

    now = datetime.now(timezone.utc).isoformat()
    await subscriptions_col.update_one(
        {"_id": sub["_id"]},
        {"$set": {"status": "canceled", "canceled_at": now}}
    )

    # Decrement subscriber count (floor at 0)
    await strategies_col.update_one(
        {"id": strategy_id, "subscriber_count": {"$gt": 0}},
        {"$inc": {"subscriber_count": -1}}
    )

    return {"message": "Unsubscribed successfully", "strategy_id": strategy_id}


@router.get("/me/strategies")
async def my_subscribed_strategies(user: dict = Depends(get_current_user)):
    """List strategies the current user is subscribed to."""
    cursor = subscriptions_col.find(
        {"user_id": user["id"], "status": "active"}, {"_id": 0}
    ).sort("subscribed_at", -1)
    subs = await cursor.to_list(length=100)

    # Enrich with strategy details
    strategy_ids = [s["strategy_id"] for s in subs]
    strategies = {}
    if strategy_ids:
        cursor2 = strategies_col.find({"id": {"$in": strategy_ids}}, {"_id": 0})
        async for s in cursor2:
            strategies[s["id"]] = s

    result = []
    for sub in subs:
        strat = strategies.get(sub["strategy_id"])
        result.append({
            **sub,
            "strategy": strat,
        })

    return {"subscriptions": result, "total": len(result)}


# ═══════════════════════════════════════════
#  REVIEWS
# ═══════════════════════════════════════════

@router.post("/strategies/{strategy_id}/review")
async def add_review(strategy_id: str, body: ReviewCreate, user: dict = Depends(get_current_user)):
    """Add a rating + review for a strategy."""
    strategy = await _get_strategy_or_404(strategy_id)

    if strategy["creator_id"] == user["id"]:
        raise HTTPException(status_code=400, detail="Cannot review your own strategy")

    # Check if user already reviewed
    existing = await reviews_col.find_one(
        {"strategy_id": strategy_id, "user_id": user["id"]}
    )
    if existing:
        raise HTTPException(status_code=409, detail="You have already reviewed this strategy")

    now = datetime.now(timezone.utc).isoformat()
    review = {
        "id": str(uuid.uuid4()),
        "strategy_id": strategy_id,
        "user_id": user["id"],
        "user_name": user.get("name", "Anonymous"),
        "rating": body.rating,
        "comment": body.comment.strip(),
        "created_at": now,
    }
    await reviews_col.insert_one(review)

    # Recalculate average rating
    pipeline = [
        {"$match": {"strategy_id": strategy_id}},
        {"$group": {"_id": None, "avg": {"$avg": "$rating"}, "count": {"$sum": 1}}},
    ]
    agg = await reviews_col.aggregate(pipeline).to_list(length=1)
    if agg:
        await strategies_col.update_one(
            {"id": strategy_id},
            {"$set": {"avg_rating": round(agg[0]["avg"], 2), "review_count": agg[0]["count"]}}
        )

    return {"message": "Review added", "review": _sanitize(review)}


# ═══════════════════════════════════════════
#  CREATOR: My Strategies
# ═══════════════════════════════════════════

@router.get("/me/created")
async def my_created_strategies(user: dict = Depends(get_current_user)):
    """List strategies the current user has created."""
    cursor = strategies_col.find(
        {"creator_id": user["id"]}, {"_id": 0}
    ).sort("created_at", -1)
    items = await cursor.to_list(length=100)
    return {"strategies": items, "total": len(items)}


# ═══════════════════════════════════════════
#  FEATURED STRATEGIES (public, no auth)
# ═══════════════════════════════════════════

@router.get("/featured")
async def featured_strategies():
    """Return published featured strategies with their performance data."""
    query = {"status": "published", "is_public": True, "featured": True}
    cursor = strategies_col.find(query, {"_id": 0}).sort("subscriber_count", -1).limit(6)
    items = await cursor.to_list(length=6)

    # Enrich with latest performance
    for s in items:
        perf = await performance_col.find_one(
            {"strategy_id": s["id"]}, {"_id": 0}, sort=[("uploaded_at", -1)]
        )
        s["_perf"] = perf or {}

    return {"strategies": items}


# ═══════════════════════════════════════════
#  COPY STRATEGY
# ═══════════════════════════════════════════

@router.post("/strategies/{strategy_id}/copy")
async def copy_strategy(strategy_id: str, user: dict = Depends(get_current_user)):
    """Copy a published strategy into the user's own collection."""
    source = await _get_strategy_or_404(strategy_id)

    if source["status"] != "published":
        raise HTTPException(status_code=400, detail="Can only copy published strategies")

    now = datetime.now(timezone.utc).isoformat()
    new_strategy = {
        "id": str(uuid.uuid4()),
        "creator_id": user["id"],
        "creator_name": user.get("name", "Unknown"),
        "name": f"{source['name']} (Copy)",
        "description": source.get("description", ""),
        "category": source.get("category", "other"),
        "parameters": source.get("parameters", {}),
        "created_at": now,
        "updated_at": now,
        "is_public": False,
        "status": "draft",
        "subscriber_count": 0,
        "avg_rating": 0.0,
        "review_count": 0,
        "copied_from": strategy_id,
        "featured": False,
    }
    await strategies_col.insert_one(new_strategy)
    return {"message": "Strategy copied to your collection", "strategy": _sanitize(new_strategy)}
