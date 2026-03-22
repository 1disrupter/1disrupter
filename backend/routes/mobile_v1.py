"""
AlphaAI Mobile API v1
Optimized endpoints for React Native / Expo mobile app
- Versioned API (/api/v1/)
- Balanced data optimization (pagination, field selection, caching)
- Cross-platform authentication
- Push notification hooks
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Request, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import hashlib
import json
import logging

logger = logging.getLogger("AlphaAI.Mobile")

# MongoDB connection
db = None

def init_db(database):
    global db
    db = database

router = APIRouter(prefix="/api/v1", tags=["Mobile API v1"])

# ============= MODELS =============

class MobileAuthResponse(BaseModel):
    """Optimized auth response for mobile"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until expiry
    user: Dict[str, Any]

class DeviceRegistration(BaseModel):
    """Register device for push notifications"""
    device_id: str
    platform: str  # "ios", "android", "expo"
    push_token: str
    app_version: str
    os_version: Optional[str] = None
    device_model: Optional[str] = None

class PaginatedResponse(BaseModel):
    """Standard paginated response"""
    data: List[Any]
    pagination: Dict[str, Any]
    meta: Optional[Dict[str, Any]] = None

class MobileSignalResponse(BaseModel):
    """Lightweight signal for mobile"""
    id: str
    symbol: str
    type: str  # "BUY" or "SELL"
    confidence: int
    price: float
    timestamp: str
    is_new: bool = False

# ============= HELPERS =============

def generate_etag(data: Any) -> str:
    """Generate ETag for caching"""
    content = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(content.encode()).hexdigest()

def create_paginated_response(
    data: List[Any],
    page: int,
    limit: int,
    total: int,
    meta: Optional[Dict] = None
) -> Dict:
    """Create standard paginated response"""
    total_pages = (total + limit - 1) // limit
    return {
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "meta": meta or {}
    }

def select_fields(item: Dict, fields: Optional[str]) -> Dict:
    """Select only requested fields (sparse fieldsets)"""
    if not fields:
        return item
    
    field_list = [f.strip() for f in fields.split(",")]
    return {k: v for k, v in item.items() if k in field_list}

async def get_current_user_mobile(request: Request) -> dict:
    """Get current user from JWT - mobile optimized"""
    from routes.auth import get_current_user
    return await get_current_user(request)

# ============= HEALTH & CONNECTIVITY =============

@router.get("/health")
async def mobile_health_check():
    """
    Health check endpoint for mobile connectivity testing.
    Returns minimal payload for fast response.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }

@router.get("/ping")
async def mobile_ping():
    """Ultra-minimal ping for connection testing"""
    return {"pong": True}

@router.get("/config")
async def get_mobile_config():
    """
    Get mobile app configuration.
    Cached aggressively on client side.
    """
    return {
        "api_version": "1.0.0",
        "min_app_version": "1.0.0",
        "force_update": False,
        "maintenance_mode": False,
        "features": {
            "push_notifications": True,
            "biometric_auth": True,
            "offline_mode": False,
            "websocket_signals": True
        },
        "endpoints": {
            "websocket": "/ws/signals",
            "auth": "/api/v1/auth",
            "signals": "/api/v1/signals",
            "trading": "/api/v1/trading",
            "portfolio": "/api/v1/portfolio"
        },
        "refresh_intervals": {
            "signals": 30,  # seconds
            "prices": 5,
            "portfolio": 60,
            "notifications": 300
        },
        "pagination": {
            "default_limit": 20,
            "max_limit": 100
        }
    }

# ============= AUTHENTICATION (Mobile Optimized) =============

@router.post("/auth/login", response_model=MobileAuthResponse)
async def mobile_login(
    email: str = Query(...),
    password: str = Query(...),
    device_id: Optional[str] = Query(None),
    totp_code: Optional[str] = Query(None)
):
    """
    Mobile-optimized login endpoint.
    Returns token expiry in seconds for easy client-side handling.
    """
    from routes.auth import login, UserLogin
    
    credentials = UserLogin(email=email, password=password, totp_code=totp_code)
    
    # Use existing login logic
    from fastapi import BackgroundTasks
    result = await login(credentials)
    
    # Calculate expiry
    expires_in = 24 * 60 * 60  # 24 hours in seconds
    
    # Slim down user object for mobile
    user_slim = {
        "id": result.user.id,
        "email": result.user.email,
        "name": result.user.name,
        "is_pro": result.user.is_pro,
        "is_elite": result.user.is_elite,
        "is_verified": result.user.is_verified,
        "has_2fa": result.user.has_2fa
    }
    
    # Track device if provided
    if device_id:
        await db.user_devices.update_one(
            {"user_id": result.user.id, "device_id": device_id},
            {
                "$set": {
                    "last_login": datetime.now(timezone.utc),
                    "is_active": True
                }
            },
            upsert=True
        )
    
    return MobileAuthResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        user=user_slim
    )

@router.post("/auth/refresh")
async def mobile_refresh_token(
    refresh_token: str = Query(...),
    device_id: Optional[str] = Query(None)
):
    """
    Refresh access token - mobile optimized.
    """
    from routes.auth import refresh_tokens, RefreshTokenRequest
    
    request = RefreshTokenRequest(refresh_token=refresh_token)
    result = await refresh_tokens(request)
    
    expires_in = 24 * 60 * 60
    
    user_slim = {
        "id": result.user.id,
        "email": result.user.email,
        "name": result.user.name,
        "is_pro": result.user.is_pro,
        "is_elite": result.user.is_elite
    }
    
    return {
        "access_token": result.access_token,
        "refresh_token": result.refresh_token,
        "expires_in": expires_in,
        "user": user_slim
    }

@router.get("/auth/me")
async def mobile_get_profile(
    request: Request,
    fields: Optional[str] = Query(None, description="Comma-separated fields to return")
):
    """
    Get current user profile - supports field selection.
    Example: ?fields=id,name,is_pro
    """
    user = await get_current_user_mobile(request)
    
    profile = {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "is_pro": user.get("is_pro", False),
        "is_elite": user.get("is_elite", False),
        "is_verified": user.get("is_verified", False),
        "has_2fa": user.get("has_2fa", False),
        "wallet_address": user.get("wallet_address"),
        "paper_balance": user.get("paper_balance", 10000),
        "created_at": user.get("created_at", datetime.now(timezone.utc)).isoformat()
    }
    
    return select_fields(profile, fields)

# ============= SIGNALS (Mobile Optimized) =============

@router.get("/signals")
async def get_mobile_signals(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    fields: Optional[str] = Query(None),
    since: Optional[str] = Query(None, description="ISO timestamp for incremental sync"),
    if_none_match: Optional[str] = Header(None)
):
    """
    Get trading signals - mobile optimized with pagination and caching.
    
    Features:
    - Pagination with page/limit
    - Field selection with ?fields=id,symbol,type
    - Incremental sync with ?since=timestamp
    - ETag caching support
    """
    user = await get_current_user_mobile(request)
    is_pro = user.get("is_pro", False) or user.get("is_elite", False)
    
    # Build query
    query = {}
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
            query["timestamp"] = {"$gt": since_dt}
        except:
            pass
    
    # Get total count
    total = await db.signals.count_documents(query)
    
    # Get signals with pagination
    skip = (page - 1) * limit
    signals_cursor = db.signals.find(
        query, {"_id": 0}
    ).sort("timestamp", -1).skip(skip).limit(limit)
    
    signals = await signals_cursor.to_list(limit)
    
    # Apply tier-based delay for free users
    now = datetime.now(timezone.utc)
    if not is_pro:
        delay_minutes = 15
        for signal in signals:
            signal_time = signal.get("timestamp", now)
            if isinstance(signal_time, str):
                signal_time = datetime.fromisoformat(signal_time.replace('Z', '+00:00'))
            
            age = (now - signal_time).total_seconds() / 60
            if age < delay_minutes:
                signal["is_delayed"] = True
                signal["available_at"] = (signal_time + timedelta(minutes=delay_minutes)).isoformat()
    
    # Format for mobile
    mobile_signals = []
    for s in signals:
        mobile_signal = {
            "id": s.get("id", ""),
            "symbol": s.get("symbol", ""),
            "type": s.get("signal_type", s.get("type", "")),
            "confidence": s.get("confidence", 0),
            "price": s.get("price", s.get("entry_price", 0)),
            "timestamp": s.get("timestamp", now).isoformat() if isinstance(s.get("timestamp"), datetime) else s.get("timestamp", ""),
            "is_new": s.get("is_new", False),
            "is_delayed": s.get("is_delayed", False)
        }
        
        if fields:
            mobile_signal = select_fields(mobile_signal, fields)
        
        mobile_signals.append(mobile_signal)
    
    # Generate ETag
    etag = generate_etag(mobile_signals)
    
    # Check if client has cached version
    if if_none_match and if_none_match == etag:
        return JSONResponse(status_code=304, content=None)
    
    response_data = create_paginated_response(
        data=mobile_signals,
        page=page,
        limit=limit,
        total=total,
        meta={
            "is_pro": is_pro,
            "delay_minutes": 0 if is_pro else 15,
            "etag": etag
        }
    )
    
    response = JSONResponse(content=response_data)
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "private, max-age=30"
    
    return response

@router.get("/signals/latest")
async def get_latest_signal(request: Request):
    """
    Get single latest signal - ultra-lightweight endpoint.
    Ideal for widgets and quick updates.
    """
    user = await get_current_user_mobile(request)
    is_pro = user.get("is_pro", False) or user.get("is_elite", False)
    
    signal = await db.signals.find_one({}, {"_id": 0}, sort=[("timestamp", -1)])
    
    if not signal:
        return {"signal": None, "is_pro": is_pro}
    
    return {
        "signal": {
            "id": signal.get("id", ""),
            "symbol": signal.get("symbol", ""),
            "type": signal.get("signal_type", ""),
            "confidence": signal.get("confidence", 0),
            "price": signal.get("price", 0),
            "timestamp": signal.get("timestamp", datetime.now(timezone.utc)).isoformat() if isinstance(signal.get("timestamp"), datetime) else signal.get("timestamp", "")
        },
        "is_pro": is_pro
    }

# ============= PORTFOLIO (Mobile Optimized) =============

@router.get("/portfolio/summary")
async def get_portfolio_summary(
    request: Request,
    if_none_match: Optional[str] = Header(None)
):
    """
    Get portfolio summary - single endpoint for dashboard widget.
    """
    user = await get_current_user_mobile(request)
    user_id = user["id"]
    wallet = user.get("wallet_address", "")
    
    # Get paper trading stats
    paper_balance = user.get("paper_balance", 10000)
    paper_pnl = user.get("paper_pnl", 0)
    
    # Get open positions count
    open_positions = await db.trades.count_documents({
        "wallet_address": wallet,
        "status": "open",
        "is_paper": True
    })
    
    # Get today's trades
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_trades = await db.trades.count_documents({
        "wallet_address": wallet,
        "timestamp": {"$gte": today_start}
    })
    
    summary = {
        "paper_balance": round(paper_balance, 2),
        "paper_pnl": round(paper_pnl, 2),
        "paper_pnl_percent": round((paper_pnl / 10000) * 100, 2),
        "open_positions": open_positions,
        "today_trades": today_trades,
        "is_pro": user.get("is_pro", False),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    etag = generate_etag(summary)
    
    if if_none_match and if_none_match == etag:
        return JSONResponse(status_code=304, content=None)
    
    response = JSONResponse(content=summary)
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "private, max-age=60"
    
    return response

@router.get("/portfolio/positions")
async def get_portfolio_positions(
    request: Request,
    status: str = Query("open", description="open, closed, all"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50)
):
    """Get trading positions with pagination"""
    user = await get_current_user_mobile(request)
    wallet = user.get("wallet_address", "")
    
    query = {"wallet_address": wallet, "is_paper": True}
    if status != "all":
        query["status"] = status
    
    total = await db.trades.count_documents(query)
    skip = (page - 1) * limit
    
    positions = await db.trades.find(
        query, {"_id": 0}
    ).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
    
    # Slim down for mobile
    mobile_positions = []
    for p in positions:
        mobile_positions.append({
            "id": p.get("id", ""),
            "symbol": p.get("symbol", ""),
            "side": p.get("side", ""),
            "amount": p.get("amount", 0),
            "entry_price": p.get("entry_price", 0),
            "current_price": p.get("current_price", p.get("entry_price", 0)),
            "pnl": p.get("pnl", 0),
            "pnl_percent": p.get("pnl_percent", 0),
            "status": p.get("status", ""),
            "timestamp": p.get("timestamp", datetime.now(timezone.utc)).isoformat() if isinstance(p.get("timestamp"), datetime) else p.get("timestamp", "")
        })
    
    return create_paginated_response(
        data=mobile_positions,
        page=page,
        limit=limit,
        total=total
    )

# ============= TRADING (Mobile Optimized) =============

@router.post("/trading/execute")
async def mobile_execute_trade(
    request: Request,
    symbol: str = Query(...),
    side: str = Query(..., description="BUY or SELL"),
    amount: float = Query(..., gt=0),
    signal_id: Optional[str] = Query(None)
):
    """
    Execute a trade - mobile optimized.
    Returns minimal confirmation payload.
    """
    user = await get_current_user_mobile(request)
    wallet = user.get("wallet_address", "demo_" + user["id"][:8])
    
    # Get current price (simplified)
    prices = {"BTC": 67000, "ETH": 3500, "SOL": 145}
    price = prices.get(symbol, 100)
    
    trade_value = amount * price
    paper_balance = user.get("paper_balance", 10000)
    
    if side == "BUY" and trade_value > paper_balance:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Create trade
    import uuid
    trade_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    trade = {
        "id": trade_id,
        "wallet_address": wallet,
        "user_id": user["id"],
        "symbol": symbol,
        "side": side,
        "amount": amount,
        "entry_price": price,
        "current_price": price,
        "value": trade_value,
        "pnl": 0,
        "pnl_percent": 0,
        "status": "open",
        "is_paper": True,
        "is_live": False,
        "signal_id": signal_id,
        "timestamp": now,
        "created_at": now
    }
    
    await db.trades.insert_one(trade)
    
    # Update balance
    if side == "BUY":
        new_balance = paper_balance - trade_value
    else:
        new_balance = paper_balance + trade_value
    
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"paper_balance": new_balance}}
    )
    
    logger.info(f"Mobile trade executed: {symbol} {side} {amount} by {user['email']}")
    
    return {
        "success": True,
        "trade_id": trade_id,
        "symbol": symbol,
        "side": side,
        "amount": amount,
        "price": price,
        "value": round(trade_value, 2),
        "new_balance": round(new_balance, 2),
        "timestamp": now.isoformat()
    }

# ============= PUSH NOTIFICATIONS =============

@router.post("/devices/register")
async def register_device(
    device: DeviceRegistration,
    request: Request
):
    """
    Register device for push notifications.
    Supports iOS, Android, and Expo push tokens.
    """
    user = await get_current_user_mobile(request)
    
    now = datetime.now(timezone.utc)
    
    device_record = {
        "user_id": user["id"],
        "device_id": device.device_id,
        "platform": device.platform,
        "push_token": device.push_token,
        "app_version": device.app_version,
        "os_version": device.os_version,
        "device_model": device.device_model,
        "is_active": True,
        "registered_at": now,
        "last_active": now
    }
    
    # Upsert device
    await db.user_devices.update_one(
        {"user_id": user["id"], "device_id": device.device_id},
        {"$set": device_record},
        upsert=True
    )
    
    logger.info(f"Device registered: {device.platform} for user {user['email']}")
    
    return {
        "success": True,
        "message": "Device registered for push notifications",
        "device_id": device.device_id
    }

@router.delete("/devices/{device_id}")
async def unregister_device(
    device_id: str,
    request: Request
):
    """Unregister device from push notifications"""
    user = await get_current_user_mobile(request)
    
    result = await db.user_devices.delete_one({
        "user_id": user["id"],
        "device_id": device_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {"success": True, "message": "Device unregistered"}

@router.get("/devices")
async def list_devices(request: Request):
    """List user's registered devices"""
    user = await get_current_user_mobile(request)
    
    devices = await db.user_devices.find(
        {"user_id": user["id"]},
        {"_id": 0, "push_token": 0}  # Don't expose push token
    ).to_list(10)
    
    return {
        "devices": devices,
        "count": len(devices)
    }

@router.put("/devices/{device_id}/token")
async def update_push_token(
    device_id: str,
    push_token: str = Query(...),
    request: Request = None
):
    """Update push token for a device (tokens can change)"""
    user = await get_current_user_mobile(request)
    
    result = await db.user_devices.update_one(
        {"user_id": user["id"], "device_id": device_id},
        {
            "$set": {
                "push_token": push_token,
                "last_active": datetime.now(timezone.utc)
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {"success": True, "message": "Push token updated"}

# ============= NOTIFICATION PREFERENCES =============

@router.get("/notifications/preferences")
async def get_notification_preferences(request: Request):
    """Get user's notification preferences"""
    user = await get_current_user_mobile(request)
    
    prefs = await db.notification_preferences.find_one(
        {"user_id": user["id"]},
        {"_id": 0}
    )
    
    # Default preferences
    default_prefs = {
        "user_id": user["id"],
        "push_enabled": True,
        "signal_alerts": True,
        "signal_min_confidence": 70,
        "price_alerts": True,
        "trade_confirmations": True,
        "daily_summary": True,
        "weekly_report": True,
        "marketing": False,
        "quiet_hours": {
            "enabled": False,
            "start": "22:00",
            "end": "08:00",
            "timezone": "UTC"
        }
    }
    
    # Merge existing preferences with defaults
    if prefs:
        merged = {**default_prefs, **prefs}
        # Ensure quiet_hours is properly merged
        if "quiet_hours" not in prefs:
            merged["quiet_hours"] = default_prefs["quiet_hours"]
        return merged
    
    return default_prefs

@router.put("/notifications/preferences")
async def update_notification_preferences(
    request: Request,
    push_enabled: Optional[bool] = Query(None),
    signal_alerts: Optional[bool] = Query(None),
    signal_min_confidence: Optional[int] = Query(None, ge=0, le=100),
    price_alerts: Optional[bool] = Query(None),
    trade_confirmations: Optional[bool] = Query(None),
    daily_summary: Optional[bool] = Query(None),
    weekly_report: Optional[bool] = Query(None),
    marketing: Optional[bool] = Query(None)
):
    """Update notification preferences"""
    user = await get_current_user_mobile(request)
    
    updates = {}
    if push_enabled is not None:
        updates["push_enabled"] = push_enabled
    if signal_alerts is not None:
        updates["signal_alerts"] = signal_alerts
    if signal_min_confidence is not None:
        updates["signal_min_confidence"] = signal_min_confidence
    if price_alerts is not None:
        updates["price_alerts"] = price_alerts
    if trade_confirmations is not None:
        updates["trade_confirmations"] = trade_confirmations
    if daily_summary is not None:
        updates["daily_summary"] = daily_summary
    if weekly_report is not None:
        updates["weekly_report"] = weekly_report
    if marketing is not None:
        updates["marketing"] = marketing
    
    if updates:
        updates["updated_at"] = datetime.now(timezone.utc)
        await db.notification_preferences.update_one(
            {"user_id": user["id"]},
            {"$set": updates},
            upsert=True
        )
    
    return {"success": True, "updated": list(updates.keys())}

# ============= METRICS (Mobile Dashboard) =============

@router.get("/metrics/summary")
async def get_mobile_metrics_summary(
    request: Request,
    days: int = Query(7, ge=1, le=90)
):
    """
    Get performance metrics summary for mobile dashboard.
    Simplified single-endpoint for overview widget.
    """
    user = await get_current_user_mobile(request)
    wallet = user.get("wallet_address", "")
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Get trades for period
    trades = await db.trades.find({
        "wallet_address": wallet,
        "is_paper": True,
        "timestamp": {"$gte": cutoff}
    }, {"_id": 0}).to_list(1000)
    
    if not trades:
        return {
            "period_days": days,
            "total_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "best_trade": 0,
            "worst_trade": 0
        }
    
    # Calculate metrics
    total_pnl = sum(t.get("pnl", 0) or 0 for t in trades)
    winning = [t for t in trades if (t.get("pnl") or 0) > 0]
    pnls = [t.get("pnl", 0) or 0 for t in trades]
    
    return {
        "period_days": days,
        "total_trades": len(trades),
        "win_rate": round(len(winning) / len(trades) * 100, 1) if trades else 0,
        "total_pnl": round(total_pnl, 2),
        "best_trade": round(max(pnls), 2) if pnls else 0,
        "worst_trade": round(min(pnls), 2) if pnls else 0
    }
