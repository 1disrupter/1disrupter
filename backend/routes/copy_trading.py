"""
AlphaAI Copy Trading API Routes
Follow traders, manage copy settings, approve/reject manual trades.
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field

from routes.auth import get_current_user
from services.copy_trading_service import (
    follow_trader, unfollow_trader, update_settings,
    get_following, get_followers, get_pending_trades,
    approve_trade, reject_trade, init_db as init_copy_db
)

logger = logging.getLogger("AlphaAI.CopyTrading.Routes")

router = APIRouter(prefix="/api/copy", tags=["copy-trading"])

db = None


def init_db(database):
    global db
    db = database
    init_copy_db(database)


# ============= REQUEST MODELS =============

class FollowRequest(BaseModel):
    trader_id: str
    mode: str = Field(default="auto", pattern="^(auto|manual)$")
    allocation_percent: float = Field(default=10, ge=1, le=100)
    max_per_trade: float = Field(default=500, ge=1, le=100000)


class UpdateSettingsRequest(BaseModel):
    relationship_id: str
    mode: Optional[str] = None
    allocation_percent: Optional[float] = Field(default=None, ge=1, le=100)
    max_per_trade: Optional[float] = Field(default=None, ge=1, le=100000)
    status: Optional[str] = None


# ============= ENDPOINTS =============

@router.post("/follow")
async def follow_trader_endpoint(request: FollowRequest, user: dict = Depends(get_current_user)):
    """Follow a trader to copy their trades. Pro/Elite only."""
    result = await follow_trader(
        copier_id=user["id"],
        trader_id=request.trader_id,
        mode=request.mode,
        allocation_percent=request.allocation_percent,
        max_per_trade=request.max_per_trade
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.delete("/unfollow/{relationship_id}")
async def unfollow_trader_endpoint(relationship_id: str, user: dict = Depends(get_current_user)):
    """Unfollow a trader and stop copying their trades."""
    result = await unfollow_trader(relationship_id, user["id"])
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.put("/settings")
async def update_settings_endpoint(request: UpdateSettingsRequest, user: dict = Depends(get_current_user)):
    """Update copy trading settings (mode, allocation %, max per trade)."""
    result = await update_settings(
        relationship_id=request.relationship_id,
        copier_id=user["id"],
        mode=request.mode,
        allocation_percent=request.allocation_percent,
        max_per_trade=request.max_per_trade,
        status=request.status
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/following")
async def get_following_endpoint(user: dict = Depends(get_current_user)):
    """List all traders the current user is following."""
    following = await get_following(user["id"])
    return {"success": True, "following": following, "count": len(following)}


@router.get("/followers")
async def get_followers_endpoint(user: dict = Depends(get_current_user)):
    """List all followers of the current user."""
    followers = await get_followers(user["id"])
    return {"success": True, "followers": followers, "count": len(followers)}


@router.get("/pending")
async def get_pending_trades_endpoint(user: dict = Depends(get_current_user)):
    """Get pending copy trades awaiting manual approval."""
    pending = await get_pending_trades(user["id"])
    return {"success": True, "pending_trades": pending, "count": len(pending)}


@router.post("/approve/{trade_id}")
async def approve_trade_endpoint(trade_id: str, user: dict = Depends(get_current_user)):
    """Approve a pending manual copy trade."""
    result = await approve_trade(trade_id, user["id"])
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/reject/{trade_id}")
async def reject_trade_endpoint(trade_id: str, user: dict = Depends(get_current_user)):
    """Reject a pending manual copy trade."""
    result = await reject_trade(trade_id, user["id"])
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
