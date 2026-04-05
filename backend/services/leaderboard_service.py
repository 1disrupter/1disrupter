"""
AlphaAI Leaderboard Service
Calculates and manages public trader rankings.
"""
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

logger = logging.getLogger("AlphaAI.Leaderboard")

# Database reference
db = None

def init_db(database):
    global db
    db = database

class TimePeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"

class SortMetric(str, Enum):
    PNL = "pnl"
    WIN_RATE = "win_rate"
    ROI = "roi"
    TOTAL_TRADES = "total_trades"

class TraderStats(BaseModel):
    user_id: str
    display_name: str
    avatar_url: Optional[str] = None
    is_public: bool = True
    is_pro: bool = False
    is_elite: bool = False
    stats: Dict[str, Any] = Field(default_factory=dict)
    period_stats: Dict[str, Dict] = Field(default_factory=dict)
    rank: Dict[str, int] = Field(default_factory=dict)
    followers_count: int = 0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LeaderboardService:
    """Service for managing trader leaderboard and rankings"""
    
    def __init__(self):
        pass
    
    async def get_leaderboard(
        self,
        period: TimePeriod = TimePeriod.ALL_TIME,
        sort_by: SortMetric = SortMetric.PNL,
        limit: int = 50,
        offset: int = 0,
        is_pro_user: bool = False
    ) -> Dict[str, Any]:
        """Get leaderboard rankings"""
        
        # Build sort field
        if period == TimePeriod.ALL_TIME:
            sort_field = f"stats.total_{sort_by.value}" if sort_by != SortMetric.WIN_RATE else "stats.win_rate"
        else:
            sort_field = f"period_stats.{period.value}.{sort_by.value}"
        
        # For non-pro users, limit to top 10
        if not is_pro_user:
            limit = min(limit, 10)
        
        # Query traders with public profiles
        pipeline = [
            {"$match": {"is_public": True}},
            {"$sort": {sort_field: -1}},
            {"$skip": offset},
            {"$limit": limit},
            {"$project": {
                "_id": 0,
                "user_id": 1,
                "display_name": 1,
                "avatar_url": 1,
                "is_pro": 1,
                "is_elite": 1,
                "stats": 1 if is_pro_user else {
                    "total_pnl": "$stats.total_pnl",
                    "win_rate": "$stats.win_rate",
                    "total_trades": "$stats.total_trades"
                },
                "period_stats": 1 if is_pro_user else {period.value: f"$period_stats.{period.value}"},
                "followers_count": 1,
                "rank": 1
            }}
        ]
        
        traders = await db.trader_stats.aggregate(pipeline).to_list(limit)
        
        # Add rank numbers
        for i, trader in enumerate(traders):
            trader["rank_position"] = offset + i + 1
        
        # Get total count
        total = await db.trader_stats.count_documents({"is_public": True})
        
        return {
            "traders": traders,
            "total": total,
            "period": period.value,
            "sort_by": sort_by.value,
            "limit": limit,
            "offset": offset,
            "is_limited": not is_pro_user and total > 10
        }
    
    async def get_trader_profile(
        self,
        trader_id: str,
        viewer_is_pro: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Get detailed trader profile"""
        
        projection = {"_id": 0}
        
        # Non-pro users get limited info
        if not viewer_is_pro:
            projection = {
                "_id": 0,
                "user_id": 1,
                "display_name": 1,
                "avatar_url": 1,
                "is_pro": 1,
                "is_elite": 1,
                "stats.total_pnl": 1,
                "stats.win_rate": 1,
                "stats.total_trades": 1,
                "followers_count": 1
            }
        
        trader = await db.trader_stats.find_one(
            {"user_id": trader_id, "is_public": True},
            projection
        )
        
        if not trader:
            return None
        
        # Get recent trades if pro viewer
        if viewer_is_pro:
            recent_trades = await db.trades.find(
                {"user_id": trader_id},
                {"_id": 0, "id": 1, "symbol": 1, "side": 1, "pnl": 1, "timestamp": 1}
            ).sort("timestamp", -1).limit(10).to_list(10)
            trader["recent_trades"] = recent_trades
        
        return trader
    
    async def update_trader_stats(self, user_id: str):
        """Recalculate and update trader stats"""
        
        # Get user info
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "name": 1, "is_pro": 1, "is_elite": 1})
        if not user:
            return
        
        # Calculate all-time stats
        all_trades = await db.trades.find(
            {"user_id": user_id},
            {"_id": 0, "pnl": 1, "timestamp": 1}
        ).limit(2000).to_list(2000)
        
        if not all_trades:
            return
        
        total_pnl = sum(t.get("pnl", 0) for t in all_trades)
        total_trades = len(all_trades)
        wins = sum(1 for t in all_trades if t.get("pnl", 0) > 0)
        losses = total_trades - wins
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        # Calculate ROI (assuming initial paper balance of 10000)
        initial_balance = 10000
        roi = (total_pnl / initial_balance * 100) if initial_balance > 0 else 0
        
        # Calculate period stats
        now = datetime.now(timezone.utc)
        period_stats = {}
        
        for period, days in [("daily", 1), ("weekly", 7), ("monthly", 30)]:
            cutoff = now - timedelta(days=days)
            period_trades = [t for t in all_trades if t.get("timestamp", now) >= cutoff]
            
            if period_trades:
                p_pnl = sum(t.get("pnl", 0) for t in period_trades)
                p_wins = sum(1 for t in period_trades if t.get("pnl", 0) > 0)
                p_total = len(period_trades)
                p_win_rate = (p_wins / p_total * 100) if p_total > 0 else 0
                p_roi = (p_pnl / initial_balance * 100)
                
                period_stats[period] = {
                    "pnl": p_pnl,
                    "win_rate": p_win_rate,
                    "roi": p_roi,
                    "total_trades": p_total,
                    "wins": p_wins,
                    "losses": p_total - p_wins
                }
            else:
                period_stats[period] = {
                    "pnl": 0, "win_rate": 0, "roi": 0,
                    "total_trades": 0, "wins": 0, "losses": 0
                }
        
        # Update or create trader stats
        stats_doc = {
            "user_id": user_id,
            "display_name": user.get("name", f"Trader_{user_id[:8]}"),
            "is_pro": user.get("is_pro", False),
            "is_elite": user.get("is_elite", False),
            "is_public": True,
            "stats": {
                "total_pnl": total_pnl,
                "win_rate": win_rate,
                "roi_percentage": roi,
                "total_trades": total_trades,
                "wins": wins,
                "losses": losses
            },
            "period_stats": period_stats,
            "updated_at": now
        }
        
        await db.trader_stats.update_one(
            {"user_id": user_id},
            {"$set": stats_doc},
            upsert=True
        )
        
        logger.info(f"Updated stats for trader {user_id}: P&L={total_pnl:.2f}, Win Rate={win_rate:.1f}%")
    
    async def update_all_rankings(self):
        """Recalculate rankings for all traders"""
        
        # Get all traders sorted by different metrics
        metrics = ["total_pnl", "win_rate", "roi_percentage"]
        
        for metric in metrics:
            traders = await db.trader_stats.find(
                {"is_public": True}
            ).sort(f"stats.{metric}", -1).limit(5000).to_list(5000)
            
            for rank, trader in enumerate(traders, 1):
                rank_key = metric.replace("_percentage", "").replace("total_", "")
                await db.trader_stats.update_one(
                    {"user_id": trader["user_id"]},
                    {"$set": {f"rank.{rank_key}": rank}}
                )
        
        logger.info(f"Updated rankings for {len(traders)} traders")
    
    async def toggle_public_profile(self, user_id: str, is_public: bool) -> Dict[str, Any]:
        """Toggle whether a trader's profile is public on leaderboard"""
        
        result = await db.trader_stats.update_one(
            {"user_id": user_id},
            {"$set": {"is_public": is_public, "updated_at": datetime.now(timezone.utc)}},
            upsert=True
        )
        
        return {
            "success": True,
            "is_public": is_public,
            "message": f"Profile {'visible' if is_public else 'hidden'} on leaderboard"
        }
    
    async def get_user_rank(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user's current rank across all metrics"""
        
        stats = await db.trader_stats.find_one(
            {"user_id": user_id},
            {"_id": 0, "rank": 1, "stats": 1}
        )
        
        if not stats:
            return None
        
        # Get total traders for percentile
        total_traders = await db.trader_stats.count_documents({"is_public": True})
        
        ranks = stats.get("rank", {})
        percentiles = {}
        
        for metric, rank in ranks.items():
            percentile = ((total_traders - rank) / total_traders * 100) if total_traders > 0 else 0
            percentiles[metric] = round(percentile, 1)
        
        return {
            "ranks": ranks,
            "percentiles": percentiles,
            "total_traders": total_traders,
            "stats": stats.get("stats", {})
        }

# Singleton instance
leaderboard_service = LeaderboardService()

def get_leaderboard_service() -> LeaderboardService:
    return leaderboard_service
