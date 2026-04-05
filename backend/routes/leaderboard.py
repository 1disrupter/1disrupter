"""
AlphaAI Leaderboard API Routes
Public trader rankings and profiles.
"""
import os
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.leaderboard_service import (
    leaderboard_service, init_db as init_leaderboard_db,
    TimePeriod, SortMetric
)

logger = logging.getLogger("AlphaAI.Leaderboard")

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])

# Database reference
db = None

def init_db(database):
    global db
    db = database
    init_leaderboard_db(database)

# ============= REQUEST MODELS =============

class ProfileSettingsRequest(BaseModel):
    is_public: bool
    display_name: Optional[str] = None

# ============= ENDPOINTS =============

@router.get("")
async def get_leaderboard(
    period: str = Query("all_time", description="Time period: daily, weekly, monthly, all_time"),
    sort_by: str = Query("pnl", description="Sort metric: pnl, win_rate, roi, total_trades"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_tier: str = Query("free", description="User tier: free, pro, elite")
):
    """
    Get public leaderboard rankings.
    Free users see top 10 only. Pro/Elite see full leaderboard with detailed stats.
    """
    try:
        # Parse period
        try:
            time_period = TimePeriod(period)
        except ValueError:
            time_period = TimePeriod.ALL_TIME
        
        # Parse sort metric
        try:
            sort_metric = SortMetric(sort_by)
        except ValueError:
            sort_metric = SortMetric.PNL
        
        is_pro = user_tier in ["pro", "elite"]
        
        result = await leaderboard_service.get_leaderboard(
            period=time_period,
            sort_by=sort_metric,
            limit=limit,
            offset=offset,
            is_pro_user=is_pro
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trader/{trader_id}")
async def get_trader_profile(
    trader_id: str,
    user_tier: str = Query("free", description="Viewer's tier: free, pro, elite")
):
    """
    Get detailed trader profile.
    Pro/Elite users see full stats and recent trades.
    """
    is_pro = user_tier in ["pro", "elite"]
    
    profile = await leaderboard_service.get_trader_profile(trader_id, is_pro)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Trader not found or profile is private")
    
    return profile

@router.get("/me")
async def get_my_rank(
    user_id: str = Query(..., description="User ID")
):
    """Get current user's rank and stats"""
    rank_info = await leaderboard_service.get_user_rank(user_id)
    
    if not rank_info:
        # User not on leaderboard yet, return default
        return {
            "ranks": {},
            "percentiles": {},
            "total_traders": await db.trader_stats.count_documents({"is_public": True}),
            "stats": {},
            "message": "Complete some trades to appear on the leaderboard"
        }
    
    return rank_info

@router.put("/settings")
async def update_leaderboard_settings(
    request: ProfileSettingsRequest,
    user_id: str = Query(..., description="User ID")
):
    """Toggle public profile visibility on leaderboard"""
    result = await leaderboard_service.toggle_public_profile(user_id, request.is_public)
    
    # Update display name if provided
    if request.display_name:
        await db.trader_stats.update_one(
            {"user_id": user_id},
            {"$set": {"display_name": request.display_name}},
            upsert=True
        )
        result["display_name"] = request.display_name
    
    return result

@router.post("/refresh")
async def refresh_user_stats(
    user_id: str = Query(..., description="User ID")
):
    """Manually refresh a user's leaderboard stats"""
    await leaderboard_service.update_trader_stats(user_id)
    
    # Get updated stats
    stats = await db.trader_stats.find_one({"user_id": user_id}, {"_id": 0})
    
    return {
        "success": True,
        "message": "Stats refreshed",
        "stats": stats
    }

@router.post("/admin/refresh-all")
async def refresh_all_rankings(
    admin_key: str = Query(..., description="Admin key")
):
    """Admin endpoint to refresh all rankings"""
    # Simple admin check
    if admin_key != os.environ.get("ADMIN_SECRET"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Update all trader stats
    users = await db.users.find({}, {"id": 1}).to_list(10000)
    
    for user in users:
        try:
            await leaderboard_service.update_trader_stats(user["id"])
        except Exception as e:
            logger.warning(f"Failed to update stats for {user['id']}: {e}")
    
    # Update rankings
    await leaderboard_service.update_all_rankings()
    
    total_traders = await db.trader_stats.count_documents({})
    
    return {
        "success": True,
        "message": f"Refreshed stats for {len(users)} users",
        "total_traders_ranked": total_traders
    }

@router.get("/top-performers")
async def get_top_performers(
    limit: int = Query(5, ge=1, le=20)
):
    """Get top performers across different metrics for homepage display"""
    
    # Top by P&L
    top_pnl = await db.trader_stats.find(
        {"is_public": True},
        {"_id": 0, "user_id": 1, "display_name": 1, "stats.total_pnl": 1}
    ).sort("stats.total_pnl", -1).limit(limit).to_list(limit)
    
    # Top by win rate (min 10 trades)
    top_win_rate = await db.trader_stats.find(
        {"is_public": True, "stats.total_trades": {"$gte": 10}},
        {"_id": 0, "user_id": 1, "display_name": 1, "stats.win_rate": 1, "stats.total_trades": 1}
    ).sort("stats.win_rate", -1).limit(limit).to_list(limit)
    
    # Top by ROI
    top_roi = await db.trader_stats.find(
        {"is_public": True, "stats.total_trades": {"$gte": 5}},
        {"_id": 0, "user_id": 1, "display_name": 1, "stats.roi_percentage": 1}
    ).sort("stats.roi_percentage", -1).limit(limit).to_list(limit)
    
    return {
        "top_by_pnl": top_pnl,
        "top_by_win_rate": top_win_rate,
        "top_by_roi": top_roi
    }


# ============= STRATEGY LEADERBOARD =============

SORT_FIELDS = {
    "sharpe": "metrics.sharpe_ratio",
    "total_return": "metrics.total_return",
    "max_drawdown": "metrics.max_drawdown",
    "win_rate": "metrics.win_rate",
}

DEMO_STRATEGIES = [
    {"id": "demo-1", "name": "BTC Momentum Alpha", "type": "momentum", "asset": "BTC/USDT", "metrics": {"sharpe_ratio": 2.14, "total_return": 24.8, "max_drawdown": 5.2, "win_rate": 68.5, "total_trades": 312, "profit_factor": 2.1, "equity_curve": [{"day": i, "value": 100000 + i * 800 + (i % 5) * 200} for i in range(30)]}, "data_source": "mock", "updated_at": "2026-03-28T12:00:00Z"},
    {"id": "demo-2", "name": "ETH Mean Reversion", "type": "mean_reversion", "asset": "ETH/USDT", "metrics": {"sharpe_ratio": 1.87, "total_return": 18.3, "max_drawdown": 4.1, "win_rate": 62.3, "total_trades": 245, "profit_factor": 1.85, "equity_curve": [{"day": i, "value": 100000 + i * 610 + (i % 3) * 300} for i in range(30)]}, "data_source": "mock", "updated_at": "2026-03-27T10:00:00Z"},
    {"id": "demo-3", "name": "SOL Breakout Hunter", "type": "breakout", "asset": "SOL/USDT", "metrics": {"sharpe_ratio": 1.72, "total_return": 21.5, "max_drawdown": 7.8, "win_rate": 55.1, "total_trades": 189, "profit_factor": 1.62, "equity_curve": [{"day": i, "value": 100000 + i * 715 + (i % 4) * 150} for i in range(30)]}, "data_source": "mock", "updated_at": "2026-03-26T08:00:00Z"},
    {"id": "demo-4", "name": "BTC Trend Follower", "type": "momentum", "asset": "BTC/USDT", "metrics": {"sharpe_ratio": 1.55, "total_return": 15.2, "max_drawdown": 6.3, "win_rate": 59.8, "total_trades": 278, "profit_factor": 1.54, "equity_curve": [{"day": i, "value": 100000 + i * 507 + (i % 6) * 100} for i in range(30)]}, "data_source": "mock", "updated_at": "2026-03-25T14:00:00Z"},
    {"id": "demo-5", "name": "ETH Scalper Pro", "type": "mean_reversion", "asset": "ETH/USDT", "metrics": {"sharpe_ratio": 1.41, "total_return": 12.7, "max_drawdown": 3.5, "win_rate": 71.2, "total_trades": 520, "profit_factor": 1.78, "equity_curve": [{"day": i, "value": 100000 + i * 423 + (i % 3) * 250} for i in range(30)]}, "data_source": "mock", "updated_at": "2026-03-24T16:00:00Z"},
    {"id": "demo-6", "name": "Multi-Asset Momentum", "type": "momentum", "asset": "BTC/USDT", "metrics": {"sharpe_ratio": 1.28, "total_return": 9.4, "max_drawdown": 4.8, "win_rate": 57.3, "total_trades": 165, "profit_factor": 1.42, "equity_curve": [{"day": i, "value": 100000 + i * 313 + (i % 5) * 180} for i in range(30)]}, "data_source": "mock", "updated_at": "2026-03-23T11:00:00Z"},
    {"id": "demo-7", "name": "SOL Volatility Catcher", "type": "breakout", "asset": "SOL/USDT", "metrics": {"sharpe_ratio": 1.15, "total_return": 8.1, "max_drawdown": 9.2, "win_rate": 51.8, "total_trades": 142, "profit_factor": 1.31, "equity_curve": [{"day": i, "value": 100000 + i * 270 + (i % 4) * 120} for i in range(30)]}, "data_source": "mock", "updated_at": "2026-03-22T09:00:00Z"},
    {"id": "demo-8", "name": "BTC Conservative", "type": "mean_reversion", "asset": "BTC/USDT", "metrics": {"sharpe_ratio": 0.98, "total_return": 5.6, "max_drawdown": 2.1, "win_rate": 64.9, "total_trades": 98, "profit_factor": 1.55, "equity_curve": [{"day": i, "value": 100000 + i * 187 + (i % 3) * 90} for i in range(30)]}, "data_source": "mock", "updated_at": "2026-03-21T15:00:00Z"},
]


@router.get("/strategies")
async def get_strategy_leaderboard(
    sort_by: str = Query("sharpe", description="Sort field: sharpe, total_return, max_drawdown, win_rate"),
    order: str = Query("desc", description="Sort order: asc or desc"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    demo: bool = Query(False),
):
    """Get ranked list of backtested strategies."""
    if demo:
        strategies = sorted(
            DEMO_STRATEGIES,
            key=lambda s: s["metrics"].get(
                {"sharpe": "sharpe_ratio", "total_return": "total_return", "max_drawdown": "max_drawdown", "win_rate": "win_rate"}.get(sort_by, "sharpe_ratio"),
                0,
            ),
            reverse=(order == "desc"),
        )
        return {"success": True, "strategies": strategies[offset:offset + limit], "total": len(strategies), "data_source": "mock"}

    sort_field = SORT_FIELDS.get(sort_by, "metrics.sharpe_ratio")
    sort_dir = -1 if order == "desc" else 1

    total = await db.strategy_leaderboard.count_documents({})
    entries = await db.strategy_leaderboard.find(
        {}, {"_id": 0}
    ).sort(sort_field, sort_dir).skip(offset).limit(limit).to_list(limit)

    return {"success": True, "strategies": entries, "total": total, "data_source": "coingecko"}


class StrategyLeaderboardEntry(BaseModel):
    strategy_id: Optional[str] = None
    name: str
    type: str
    asset: str = "BTC/USDT"
    metrics: dict
    data_source: str = "coingecko"
    parameters: Optional[dict] = None


@router.post("/strategies")
async def add_strategy_to_leaderboard(entry: StrategyLeaderboardEntry):
    """Add or update a strategy on the leaderboard."""
    doc = {
        "id": entry.strategy_id or f"strat-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "name": entry.name,
        "type": entry.type,
        "asset": entry.asset,
        "metrics": entry.metrics,
        "data_source": entry.data_source,
        "parameters": entry.parameters or {},
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.strategy_leaderboard.update_one(
        {"id": doc["id"]},
        {"$set": doc},
        upsert=True,
    )
    return {"success": True, "id": doc["id"]}


@router.get("/strategies/{strategy_id}")
async def get_strategy_detail(strategy_id: str, demo: bool = Query(False)):
    """Get full detail for a single strategy on the leaderboard."""
    if demo:
        found = next((s for s in DEMO_STRATEGIES if s["id"] == strategy_id), None)
        if found:
            return {"success": True, "strategy": found}
        return {"success": False, "detail": "Strategy not found"}

    entry = await db.strategy_leaderboard.find_one({"id": strategy_id}, {"_id": 0})
    if not entry:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"success": True, "strategy": entry}
