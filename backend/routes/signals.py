"""
AlphaAI Signal Routes
Tiered signal API with free (15-min delay) and pro (real-time) access.
"""
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional
from datetime import datetime, timezone, timedelta
from database import db, logger
from services.signal_service import signal_service

router = APIRouter(prefix="/api")

# ============= TIERED SIGNAL API ENDPOINTS =============

@router.get("/signals/free")
async def get_free_signals():
    """Get delayed signals for free users (15-minute delay)"""
    signals = await signal_service.get_signals_for_tier("free")
    
    # If no signals exist yet, generate some
    if not signals:
        await signal_service.generate_signals()
        signals = await signal_service.get_signals_for_tier("free")
    
    return {
        "signals": signals,
        "tier": "free",
        "delay_minutes": 15,
        "refresh_rate_seconds": SIGNAL_REFRESH_RATES["free"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": "You are viewing delayed signals. Upgrade to Pro for real-time access."
    }

@router.get("/signals/pro")
async def get_pro_signals(wallet_address: str = Query(..., description="Wallet address for subscription verification")):
    """Get real-time signals for Pro subscribers"""
    # Verify Pro subscription
    investor = await db.investors.find_one({"wallet_address": wallet_address})
    if not investor:
        raise HTTPException(status_code=404, detail="Wallet not found. Please register first.")
    
    if not investor.get("is_pro") and not investor.get("is_elite"):
        raise HTTPException(
            status_code=403, 
            detail="Pro subscription required for real-time signals. Current tier: Free"
        )
    
    signals = await signal_service.get_signals_for_tier("pro", wallet_address)
    
    if not signals:
        await signal_service.generate_signals()
        signals = await signal_service.get_signals_for_tier("pro", wallet_address)
    
    tier = "elite" if investor.get("is_elite") else "pro"
    
    return {
        "signals": signals,
        "tier": tier,
        "delay_minutes": 0,
        "refresh_rate_seconds": SIGNAL_REFRESH_RATES[tier],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": f"Real-time signals active ({tier.title()} tier)"
    }

@router.get("/signals/elite")
async def get_elite_signals(wallet_address: str = Query(..., description="Wallet address for subscription verification")):
    """Get priority real-time signals for Elite subscribers"""
    investor = await db.investors.find_one({"wallet_address": wallet_address})
    if not investor:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    if not investor.get("is_elite"):
        raise HTTPException(
            status_code=403, 
            detail="Elite subscription required for priority signals"
        )
    
    signals = await signal_service.get_signals_for_tier("elite", wallet_address)
    
    if not signals:
        await signal_service.generate_signals()
        signals = await signal_service.get_signals_for_tier("elite", wallet_address)
    
    return {
        "signals": signals,
        "tier": "elite",
        "delay_minutes": 0,
        "refresh_rate_seconds": SIGNAL_REFRESH_RATES["elite"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "priority_access": True,
        "message": "Elite priority signals active - Fastest refresh rate"
    }

@router.get("/signals/tiered")
async def get_tiered_signals(wallet_address: Optional[str] = None):
    """Smart endpoint that returns appropriate signals based on user's subscription"""
    tier = "free"
    
    if wallet_address:
        investor = await db.investors.find_one({"wallet_address": wallet_address})
        if investor:
            if investor.get("is_elite"):
                tier = "elite"
            elif investor.get("is_pro"):
                tier = "pro"
    
    signals = await signal_service.get_signals_for_tier(tier, wallet_address)
    
    if not signals:
        await signal_service.generate_signals()
        signals = await signal_service.get_signals_for_tier(tier, wallet_address)
    
    return {
        "signals": signals,
        "tier": tier,
        "delay_minutes": 15 if tier == "free" else 0,
        "refresh_rate_seconds": SIGNAL_REFRESH_RATES[tier],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "is_realtime": tier != "free"
    }

@router.post("/signals/generate")
async def trigger_signal_generation(background_tasks: BackgroundTasks):
    """Manually trigger signal generation (admin use)"""
    background_tasks.add_task(signal_service.generate_signals, True)
    return {"message": "Signal generation triggered", "timestamp": datetime.now(timezone.utc).isoformat()}

@router.get("/signals/history")
async def get_signal_history(
    symbol: Optional[str] = None,
    hours: int = Query(default=24, le=168, description="Hours of history (max 168 = 7 days)"),
    limit: int = Query(default=50, le=200)
):
    """Get historical signals"""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    query = {"generated_at": {"$gte": cutoff}}
    if symbol:
        query["symbol"] = symbol.upper()
    
    signals = await db.trading_signals.find(
        query, 
        {"_id": 0}
    ).sort("generated_at", -1).limit(limit).to_list(limit)
    
    # Convert datetime to string
    for signal in signals:
        if isinstance(signal.get("generated_at"), datetime):
            signal["generated_at"] = signal["generated_at"].isoformat()
        if isinstance(signal.get("expires_at"), datetime):
            signal["expires_at"] = signal["expires_at"].isoformat()
    
    return {
        "signals": signals,
        "count": len(signals),
        "hours": hours,
        "symbol_filter": symbol
    }

@router.get("/subscription/tier")
async def get_user_tier(wallet_address: str):
    """Get user's current subscription tier and signal access"""
    investor = await db.investors.find_one({"wallet_address": wallet_address})
    
    if not investor:
        return {
            "wallet_address": wallet_address,
            "tier": "unregistered",
            "signal_delay_minutes": 15,
            "refresh_rate_seconds": SIGNAL_REFRESH_RATES["free"],
            "features": ["delayed_signals"],
            "message": "Register wallet to access signals"
        }
    
    if investor.get("is_elite"):
        tier = "elite"
        features = ["realtime_signals", "priority_refresh", "email_alerts", "push_notifications", "custom_alerts", "priority_support"]
    elif investor.get("is_pro"):
        tier = "pro"
        features = ["realtime_signals", "email_alerts", "push_notifications", "ai_analysis"]
    else:
        tier = "free"
        features = ["delayed_signals", "basic_analysis"]
    
    return {
        "wallet_address": wallet_address,
        "tier": tier,
        "is_pro": investor.get("is_pro", False),
        "is_elite": investor.get("is_elite", False),
        "pro_since": investor.get("pro_since"),
        "signal_delay_minutes": 0 if tier != "free" else 15,
        "refresh_rate_seconds": SIGNAL_REFRESH_RATES.get(tier, 300),
        "features": features
    }

