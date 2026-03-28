"""
AlphaAI Notification Routes
Push notification preferences and device management.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
import uuid
from database import db, logger

router = APIRouter(prefix="/api")

class NotificationPreferencesUpdate(BaseModel):
    push_enabled: Optional[bool] = None
    signal_alerts: Optional[bool] = None
    high_confidence_alerts: Optional[bool] = None
    trade_confirmations: Optional[bool] = None
    price_alerts: Optional[bool] = None
    daily_summary: Optional[bool] = None
    weekly_report: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None  # "22:00"
    quiet_hours_end: Optional[str] = None    # "08:00"

@router.get("/notifications/preferences")
async def get_notification_preferences(wallet_address: str = Query(...)):
    """Get notification preferences for a user"""
    prefs = await db.notification_preferences.find_one(
        {"user_id": wallet_address},
        {"_id": 0}
    )
    
    if not prefs:
        # Return defaults
        prefs = {
            "user_id": wallet_address,
            "push_enabled": True,
            "signal_alerts": True,
            "high_confidence_alerts": True,
            "trade_confirmations": True,
            "price_alerts": True,
            "daily_summary": False,
            "weekly_report": False,
            "quiet_hours": {
                "enabled": False,
                "start": "22:00",
                "end": "08:00"
            }
        }
    
    return prefs

@router.put("/notifications/preferences")
async def update_notification_preferences(
    wallet_address: str = Query(...),
    prefs: NotificationPreferencesUpdate = None
):
    """Update notification preferences for a user"""
    update_data = {}
    
    if prefs:
        if prefs.push_enabled is not None:
            update_data["push_enabled"] = prefs.push_enabled
        if prefs.signal_alerts is not None:
            update_data["signal_alerts"] = prefs.signal_alerts
        if prefs.high_confidence_alerts is not None:
            update_data["high_confidence_alerts"] = prefs.high_confidence_alerts
        if prefs.trade_confirmations is not None:
            update_data["trade_confirmations"] = prefs.trade_confirmations
        if prefs.price_alerts is not None:
            update_data["price_alerts"] = prefs.price_alerts
        if prefs.daily_summary is not None:
            update_data["daily_summary"] = prefs.daily_summary
        if prefs.weekly_report is not None:
            update_data["weekly_report"] = prefs.weekly_report
        if prefs.quiet_hours_enabled is not None:
            update_data["quiet_hours.enabled"] = prefs.quiet_hours_enabled
        if prefs.quiet_hours_start is not None:
            update_data["quiet_hours.start"] = prefs.quiet_hours_start
        if prefs.quiet_hours_end is not None:
            update_data["quiet_hours.end"] = prefs.quiet_hours_end
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        await db.notification_preferences.update_one(
            {"user_id": wallet_address},
            {"$set": update_data},
            upsert=True
        )
    
    return await get_notification_preferences(wallet_address)

@router.get("/notifications/config")
async def get_notification_config():
    """Get notification configuration (thresholds, etc.)"""
    # HIGH_CONFIDENCE_THRESHOLD is imported at the module level
    return {
        "high_confidence_threshold": 75,  # Default threshold
        "notification_types": [
            {"id": "signal_alerts", "name": "Signal Alerts", "description": "All trading signals"},
            {"id": "high_confidence_alerts", "name": "High-Confidence Alerts", "description": "Signals with 75%+ confidence"},
            {"id": "trade_confirmations", "name": "Trade Confirmations", "description": "Trade execution confirmations"},
            {"id": "price_alerts", "name": "Price Alerts", "description": "Price target notifications"},
            {"id": "daily_summary", "name": "Daily Summary", "description": "Daily trading summary"},
            {"id": "weekly_report", "name": "Weekly Report", "description": "Weekly performance report"}
        ]
    }

@router.post("/notifications/test")
async def test_notification(wallet_address: str = Query(...)):
    """Send a test notification to verify setup"""
    # push_service is imported at module level below
    from services.push_notifications import get_push_service
    ps = get_push_service()
    
    result = await ps.send_to_user(
        user_id=wallet_address,
        title="🔔 Test Notification",
        body="Push notifications are working! You'll receive alerts for high-confidence signals.",
        data={"type": "test", "screen": "dashboard"}
    )
    
    return {
        "success": result.get("success", False),
        "message": "Test notification sent" if result.get("success") else result.get("reason", "Failed to send"),
        "details": result
    }

# Include auth router
from routes.auth import router as auth_router, init_db as init_auth_db
from routes.metrics import router as metrics_router, init_db as init_metrics_db
from routes.demo import router as demo_router, init_db as init_demo_db
from routes.referrals import router as referrals_router, init_db as init_referrals_db
from routes.mobile_v1 import router as mobile_v1_router, init_db as init_mobile_db
from routes.admin import router as admin_router, init_db as init_admin_db
from routes.orders import router as orders_router, init_db as init_orders_db
from routes.leaderboard import router as leaderboard_router, init_db as init_leaderboard_db
from routes.copy_trading import router as copy_trading_router, init_db as init_copy_trading_db
from services.push_notifications import push_service, init_db as init_push_db, HIGH_CONFIDENCE_THRESHOLD

# Initialize auth database
init_auth_db(db)
init_metrics_db(db)
init_demo_db(db)
init_referrals_db(db)
init_mobile_db(db)
init_admin_db(db)
init_orders_db(db)
init_leaderboard_db(db)
init_copy_trading_db(db)
init_push_db(db)  # Initialize push notification service

# Include router and middleware
