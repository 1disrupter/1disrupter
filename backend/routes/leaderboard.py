"""
AlphaAI Leaderboard API Routes
Public trader rankings and profiles.
"""
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
    if admin_key != "alphaai_admin_2026":
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
