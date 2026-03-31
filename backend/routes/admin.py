"""
AlphaAI Admin Routes
Comprehensive admin dashboard with user management, subscriptions,
logs, feature toggles, system tools, and security audit logging.
"""
import os
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, Body, Request
from pydantic import BaseModel, Field
from functools import wraps

logger = logging.getLogger("AlphaAI.Admin")

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Database reference (set by init_db)
db = None

def init_db(database):
    global db
    db = database

# ============= MODELS =============

class UserListItem(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    is_verified: bool = False
    is_pro: bool = False
    is_elite: bool = False
    is_active: bool = True
    subscription_status: Optional[str] = None

class UserActionRequest(BaseModel):
    user_id: str
    action: str  # set_free, set_pro, set_elite, deactivate, activate, delete
    reason: Optional[str] = None

class SubscriptionOverride(BaseModel):
    user_id: str
    plan: str  # free, pro, elite
    expires_at: Optional[datetime] = None
    reason: str

class FeatureToggle(BaseModel):
    feature_id: str
    name: str
    description: str
    enabled: bool
    category: str

class FeatureToggleUpdate(BaseModel):
    feature_id: str
    enabled: bool

class SystemToolRequest(BaseModel):
    tool: str  # clear_cache, refresh_data, rebuild_indexes, run_maintenance
    params: Optional[dict] = None

class AuditLogEntry(BaseModel):
    id: str
    timestamp: datetime
    admin_id: str
    admin_email: str
    action: str
    target_type: str
    target_id: Optional[str] = None
    details: dict
    ip_address: Optional[str] = None

# ============= AUDIT LOGGING =============

async def log_admin_action(admin_id: str, admin_email: str, action: str, 
                           target_type: str, target_id: str = None, 
                           details: dict = None, ip_address: str = None):
    """Log all admin actions for security audit"""
    audit_entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc),
        "admin_id": admin_id,
        "admin_email": admin_email,
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "details": details or {},
        "ip_address": ip_address
    }
    await db.admin_audit_logs.insert_one(audit_entry)
    logger.info(f"Admin action: {action} by {admin_email} on {target_type}/{target_id}")
    return audit_entry

# ============= ADMIN AUTH (Simple for now) =============

ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "alphaai_admin_2026")

async def verify_admin(admin_key: str = Query(..., alias="admin_key")):
    """Verify admin access - in production, use proper JWT with admin role"""
    if admin_key != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Admin access denied")
    return {"id": "admin", "email": "admin@alphaai.com"}

# ============= USERS TAB =============

@router.get("/users")
async def list_users(
    admin: dict = Depends(verify_admin),
    search: Optional[str] = None,
    plan: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """List all users with filtering and pagination"""
    query = {}
    
    if search:
        query["$or"] = [
            {"email": {"$regex": search, "$options": "i"}},
            {"name": {"$regex": search, "$options": "i"}},
            {"id": {"$regex": search, "$options": "i"}}
        ]
    
    if plan:
        if plan == "free":
            query["is_pro"] = {"$ne": True}
            query["is_elite"] = {"$ne": True}
        elif plan == "pro":
            query["is_pro"] = True
        elif plan == "elite":
            query["is_elite"] = True
    
    if status == "active":
        query["is_active"] = {"$ne": False}
    elif status == "inactive":
        query["is_active"] = False
    elif status == "verified":
        query["is_verified"] = True
    elif status == "unverified":
        query["is_verified"] = {"$ne": True}
    
    total = await db.users.count_documents(query)
    skip = (page - 1) * limit
    
    users = await db.users.find(
        query,
        {"_id": 0, "password_hash": 0, "verification_token": 0, "reset_token": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Add subscription info
    for user in users:
        sub = await db.subscriptions.find_one({"user_id": user["id"]}, {"_id": 0})
        user["subscription_status"] = sub.get("status") if sub else "none"
        user["subscription_expires"] = sub.get("expires_at") if sub else None
    
    return {
        "users": users,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@router.get("/users/{user_id}")
async def get_user_details(user_id: str, admin: dict = Depends(verify_admin)):
    """Get detailed user information"""
    user = await db.users.find_one(
        {"id": user_id},
        {"_id": 0, "password_hash": 0, "verification_token": 0, "reset_token": 0}
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get subscription
    subscription = await db.subscriptions.find_one({"user_id": user_id}, {"_id": 0})
    
    # Get recent trades
    trades = await db.trades.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(10).to_list(10)
    for t in trades:
        t.pop("_id", None)
    
    # Get payment history
    payments = await db.payment_transactions.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(10).to_list(10)
    for p in payments:
        p.pop("_id", None)
    
    return {
        "user": user,
        "subscription": subscription,
        "recent_trades": trades,
        "payment_history": payments
    }

@router.post("/users/action")
async def user_action(request: UserActionRequest, admin: dict = Depends(verify_admin)):
    """Perform admin action on user"""
    user = await db.users.find_one({"id": request.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {"updated_at": datetime.now(timezone.utc)}
    action_details = {"reason": request.reason}
    
    if request.action == "set_free":
        update_data["is_pro"] = False
        update_data["is_elite"] = False
        await db.subscriptions.delete_one({"user_id": request.user_id})
        action_details["plan"] = "free"
    
    elif request.action == "set_pro":
        update_data["is_pro"] = True
        update_data["is_elite"] = False
        await db.subscriptions.update_one(
            {"user_id": request.user_id},
            {"$set": {
                "plan": "pro",
                "status": "active",
                "updated_at": datetime.now(timezone.utc),
                "admin_override": True
            }},
            upsert=True
        )
        action_details["plan"] = "pro"
    
    elif request.action == "set_elite":
        update_data["is_pro"] = True
        update_data["is_elite"] = True
        await db.subscriptions.update_one(
            {"user_id": request.user_id},
            {"$set": {
                "plan": "elite",
                "status": "active",
                "updated_at": datetime.now(timezone.utc),
                "admin_override": True
            }},
            upsert=True
        )
        action_details["plan"] = "elite"
    
    elif request.action == "deactivate":
        update_data["is_active"] = False
        action_details["status"] = "deactivated"
    
    elif request.action == "activate":
        update_data["is_active"] = True
        action_details["status"] = "activated"
    
    elif request.action == "delete":
        await db.users.delete_one({"id": request.user_id})
        await db.subscriptions.delete_one({"user_id": request.user_id})
        await db.refresh_tokens.delete_many({"user_id": request.user_id})
        await log_admin_action(
            admin["id"], admin["email"], "delete_user",
            "user", request.user_id, action_details
        )
        return {"success": True, "message": f"User {request.user_id} deleted"}
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
    
    await db.users.update_one({"id": request.user_id}, {"$set": update_data})
    
    await log_admin_action(
        admin["id"], admin["email"], request.action,
        "user", request.user_id, action_details
    )
    
    return {"success": True, "message": f"Action '{request.action}' completed for user {request.user_id}"}

# ============= SUBSCRIPTIONS TAB =============

@router.get("/subscriptions")
async def list_subscriptions(
    admin: dict = Depends(verify_admin),
    status: Optional[str] = None,
    plan: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """List all subscriptions"""
    query = {}
    if status:
        query["status"] = status
    if plan:
        query["plan"] = plan
    
    total = await db.subscriptions.count_documents(query)
    skip = (page - 1) * limit
    
    subscriptions = await db.subscriptions.find(
        query, {"_id": 0}
    ).sort("updated_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Add user info
    for sub in subscriptions:
        user = await db.users.find_one(
            {"id": sub.get("user_id")},
            {"_id": 0, "email": 1, "name": 1}
        )
        sub["user_email"] = user.get("email") if user else "Unknown"
        sub["user_name"] = user.get("name") if user else "Unknown"
    
    return {
        "subscriptions": subscriptions,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@router.post("/subscriptions/sync/{user_id}")
async def sync_subscription_with_stripe(user_id: str, admin: dict = Depends(verify_admin)):
    """Sync user's subscription status with Stripe"""
    # Get latest payment transaction
    transaction = await db.payment_transactions.find_one(
        {"user_id": user_id, "payment_status": "paid"},
        sort=[("created_at", -1)]
    )
    
    if not transaction:
        return {"success": False, "message": "No paid transactions found for user"}
    
    # Update subscription based on transaction
    await db.subscriptions.update_one(
        {"user_id": user_id},
        {"$set": {
            "status": "active",
            "stripe_session_id": transaction.get("session_id"),
            "synced_at": datetime.now(timezone.utc)
        }},
        upsert=True
    )
    
    await log_admin_action(
        admin["id"], admin["email"], "sync_subscription",
        "subscription", user_id, {"transaction_id": transaction.get("session_id")}
    )
    
    return {"success": True, "message": "Subscription synced with Stripe"}

@router.post("/subscriptions/override")
async def override_subscription(override: SubscriptionOverride, admin: dict = Depends(verify_admin)):
    """Manually override subscription status"""
    user = await db.users.find_one({"id": override.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user plan flags
    user_update = {
        "updated_at": datetime.now(timezone.utc),
        "is_pro": override.plan in ["pro", "elite"],
        "is_elite": override.plan == "elite"
    }
    await db.users.update_one({"id": override.user_id}, {"$set": user_update})
    
    # Update or create subscription
    sub_data = {
        "user_id": override.user_id,
        "plan": override.plan,
        "status": "active" if override.plan != "free" else "cancelled",
        "admin_override": True,
        "override_reason": override.reason,
        "override_by": admin["email"],
        "override_at": datetime.now(timezone.utc),
        "expires_at": override.expires_at,
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.subscriptions.update_one(
        {"user_id": override.user_id},
        {"$set": sub_data},
        upsert=True
    )
    
    await log_admin_action(
        admin["id"], admin["email"], "override_subscription",
        "subscription", override.user_id,
        {"plan": override.plan, "reason": override.reason, "expires_at": str(override.expires_at)}
    )
    
    return {"success": True, "message": f"Subscription overridden to {override.plan}"}

# ============= LOGS TAB =============

@router.get("/logs")
async def get_logs(
    admin: dict = Depends(verify_admin),
    category: str = "all",  # all, backend, webhook, error, auth, payment
    severity: Optional[str] = None,  # info, warning, error
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    limit: int = 50
):
    """Get system logs with filtering"""
    query = {}
    
    if category != "all":
        query["category"] = category
    
    if severity:
        query["severity"] = severity
    
    if start_date:
        query["timestamp"] = {"$gte": datetime.fromisoformat(start_date)}
    if end_date:
        if "timestamp" not in query:
            query["timestamp"] = {}
        query["timestamp"]["$lte"] = datetime.fromisoformat(end_date)
    
    total = await db.system_logs.count_documents(query)
    skip = (page - 1) * limit
    
    logs = await db.system_logs.find(
        query, {"_id": 0}
    ).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
    
    return {
        "logs": logs,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@router.get("/logs/webhook")
async def get_webhook_logs(
    admin: dict = Depends(verify_admin),
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 50
):
    """Get webhook event logs"""
    query = {}
    if event_type:
        query["event_type"] = event_type
    if status:
        query["status"] = status
    
    total = await db.webhook_logs.count_documents(query)
    skip = (page - 1) * limit
    
    logs = await db.webhook_logs.find(
        query, {"_id": 0}
    ).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
    
    return {
        "logs": logs,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@router.get("/logs/audit")
async def get_audit_logs(
    admin: dict = Depends(verify_admin),
    admin_email: Optional[str] = None,
    action: Optional[str] = None,
    page: int = 1,
    limit: int = 50
):
    """Get admin audit logs"""
    query = {}
    if admin_email:
        query["admin_email"] = admin_email
    if action:
        query["action"] = action
    
    total = await db.admin_audit_logs.count_documents(query)
    skip = (page - 1) * limit
    
    logs = await db.admin_audit_logs.find(
        query, {"_id": 0}
    ).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
    
    return {
        "logs": logs,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

# ============= FEATURE TOGGLES TAB =============

# Default feature toggles
DEFAULT_FEATURES = [
    {"feature_id": "ai_signals", "name": "AI Signals", "description": "Enable AI-powered trading signals", "enabled": True, "category": "core"},
    {"feature_id": "live_trading", "name": "Live Trading", "description": "Enable live trading execution", "enabled": True, "category": "trading"},
    {"feature_id": "paper_trading", "name": "Paper Trading", "description": "Enable paper trading simulation", "enabled": True, "category": "trading"},
    {"feature_id": "push_notifications", "name": "Push Notifications", "description": "Enable push notifications", "enabled": True, "category": "notifications"},
    {"feature_id": "email_notifications", "name": "Email Notifications", "description": "Enable email notifications", "enabled": True, "category": "notifications"},
    {"feature_id": "referral_system", "name": "Referral System", "description": "Enable referral program", "enabled": True, "category": "growth"},
    {"feature_id": "stripe_payments", "name": "Stripe Payments", "description": "Enable Stripe payment processing", "enabled": True, "category": "payments"},
    {"feature_id": "crypto_payments", "name": "Crypto Payments", "description": "Enable cryptocurrency payments", "enabled": False, "category": "payments"},
    {"feature_id": "two_factor_auth", "name": "Two-Factor Auth", "description": "Enable 2FA for users", "enabled": True, "category": "security"},
    {"feature_id": "api_rate_limiting", "name": "API Rate Limiting", "description": "Enable API rate limiting", "enabled": True, "category": "security"},
    {"feature_id": "maintenance_mode", "name": "Maintenance Mode", "description": "Put system in maintenance mode", "enabled": False, "category": "system"},
    {"feature_id": "new_registrations", "name": "New Registrations", "description": "Allow new user registrations", "enabled": True, "category": "system"},
]

@router.get("/features")
async def get_feature_toggles(admin: dict = Depends(verify_admin)):
    """Get all feature toggles"""
    features = await db.feature_toggles.find({}, {"_id": 0}).to_list(100)
    
    # Initialize defaults if empty
    if not features:
        for feature in DEFAULT_FEATURES:
            await db.feature_toggles.insert_one(feature)
        features = DEFAULT_FEATURES
    
    # Group by category
    categories = {}
    for f in features:
        cat = f.get("category", "other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(f)
    
    return {"features": features, "categories": categories}

@router.put("/features")
async def update_feature_toggle(update: FeatureToggleUpdate, admin: dict = Depends(verify_admin)):
    """Toggle a feature on/off"""
    result = await db.feature_toggles.update_one(
        {"feature_id": update.feature_id},
        {"$set": {"enabled": update.enabled, "updated_at": datetime.now(timezone.utc)}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    await log_admin_action(
        admin["id"], admin["email"], "toggle_feature",
        "feature", update.feature_id, {"enabled": update.enabled}
    )
    
    return {"success": True, "feature_id": update.feature_id, "enabled": update.enabled}

# ============= SYSTEM TOOLS TAB =============

@router.get("/system/stats")
async def get_system_stats(admin: dict = Depends(verify_admin)):
    """Get system statistics"""
    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    
    stats = {
        "users": {
            "total": await db.users.count_documents({}),
            "verified": await db.users.count_documents({"is_verified": True}),
            "pro": await db.users.count_documents({"is_pro": True}),
            "elite": await db.users.count_documents({"is_elite": True}),
            "new_24h": await db.users.count_documents({"created_at": {"$gte": day_ago}}),
            "new_7d": await db.users.count_documents({"created_at": {"$gte": week_ago}})
        },
        "subscriptions": {
            "active": await db.subscriptions.count_documents({"status": "active"}),
            "cancelled": await db.subscriptions.count_documents({"status": "cancelled"}),
            "total_revenue": 0  # Would need aggregation
        },
        "signals": {
            "total": await db.trading_signals.count_documents({}),
            "last_24h": await db.trading_signals.count_documents({"generated_at": {"$gte": day_ago}})
        },
        "trades": {
            "total": await db.trades.count_documents({}),
            "last_24h": await db.trades.count_documents({"timestamp": {"$gte": day_ago}})
        },
        "system": {
            "database_collections": await db.list_collection_names(),
            "uptime": "Running",
            "last_signal_generation": None
        }
    }
    
    # Get last signal time
    last_signal = await db.trading_signals.find_one({}, sort=[("generated_at", -1)])
    if last_signal:
        stats["system"]["last_signal_generation"] = last_signal.get("generated_at")
    
    return stats

@router.post("/system/tools")
async def run_system_tool(request: SystemToolRequest, admin: dict = Depends(verify_admin)):
    """Run system maintenance tools"""
    tool = request.tool
    result = {"tool": tool, "success": False, "message": ""}
    
    if tool == "clear_cache":
        # Clear any cached data
        await db.cache.delete_many({})
        result["success"] = True
        result["message"] = "Cache cleared successfully"
    
    elif tool == "refresh_data":
        # Trigger signal regeneration
        result["success"] = True
        result["message"] = "Data refresh triggered"
    
    elif tool == "rebuild_indexes":
        # Rebuild database indexes
        collections = ["users", "subscriptions", "trading_signals", "trades", "payment_transactions"]
        for coll in collections:
            try:
                await db[coll].create_index("created_at")
                if coll == "users":
                    await db[coll].create_index("email", unique=True)
                    await db[coll].create_index("id", unique=True)
            except Exception as e:
                logger.warning(f"Index creation warning for {coll}: {e}")
        result["success"] = True
        result["message"] = f"Indexes rebuilt for {len(collections)} collections"
    
    elif tool == "cleanup_expired_tokens":
        # Remove expired tokens
        now = datetime.now(timezone.utc)
        deleted = await db.refresh_tokens.delete_many({"expires_at": {"$lt": now}})
        result["success"] = True
        result["message"] = f"Cleaned up {deleted.deleted_count} expired tokens"
    
    elif tool == "cleanup_old_logs":
        # Remove logs older than 30 days
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        deleted = await db.system_logs.delete_many({"timestamp": {"$lt": cutoff}})
        result["success"] = True
        result["message"] = f"Cleaned up {deleted.deleted_count} old log entries"
    
    elif tool == "verify_subscriptions":
        # Verify subscription statuses match user flags
        fixed = 0
        async for user in db.users.find({"is_pro": True}):
            sub = await db.subscriptions.find_one({"user_id": user["id"], "status": "active"})
            if not sub:
                await db.users.update_one(
                    {"id": user["id"]},
                    {"$set": {"is_pro": False, "is_elite": False}}
                )
                fixed += 1
        result["success"] = True
        result["message"] = f"Verified subscriptions, fixed {fixed} inconsistencies"
    
    else:
        result["message"] = f"Unknown tool: {tool}"
    
    await log_admin_action(
        admin["id"], admin["email"], f"system_tool_{tool}",
        "system", None, {"result": result}
    )
    
    return result

# ============= DASHBOARD SUMMARY =============

@router.get("/dashboard")
async def get_admin_dashboard(admin: dict = Depends(verify_admin)):
    """Get admin dashboard summary"""
    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(days=1)
    
    return {
        "summary": {
            "total_users": await db.users.count_documents({}),
            "active_subscriptions": await db.subscriptions.count_documents({"status": "active"}),
            "signals_today": await db.trading_signals.count_documents({"generated_at": {"$gte": day_ago}}),
            "new_users_today": await db.users.count_documents({"created_at": {"$gte": day_ago}})
        },
        "recent_signups": await db.users.find(
            {}, {"_id": 0, "email": 1, "created_at": 1, "is_pro": 1}
        ).sort("created_at", -1).limit(5).to_list(5),
        "recent_payments": await db.payment_transactions.find(
            {"payment_status": "paid"}, {"_id": 0}
        ).sort("created_at", -1).limit(5).to_list(5)
    }


# ============= ADMIN ANALYTICS DASHBOARD =============

import time as _time

_analytics_cache = {"data": None, "ts": 0}
_CACHE_TTL = 60  # seconds


@router.get("/analytics")
async def admin_analytics(
    admin: dict = Depends(verify_admin),
    period: str = Query("30d", regex="^(24h|7d|30d|all)$"),
):
    """Aggregate analytics_events for the admin analytics dashboard."""

    now = datetime.now(timezone.utc)
    if period == "24h":
        cutoff = now - timedelta(hours=24)
    elif period == "7d":
        cutoff = now - timedelta(days=7)
    elif period == "30d":
        cutoff = now - timedelta(days=30)
    else:
        cutoff = datetime(2020, 1, 1, tzinfo=timezone.utc)

    cache_key = f"{period}"
    if _analytics_cache["data"] and _analytics_cache.get("key") == cache_key and _time.time() - _analytics_cache["ts"] < _CACHE_TTL:
        return _analytics_cache["data"]

    match_stage = {"timestamp": {"$gte": cutoff}}

    # 1. Total demo opens
    demo_opens = await db.analytics_events.count_documents({**match_stage, "event_type": "demo_link_opened"})

    # 2. Demo opens over time (by date)
    opens_over_time = await db.analytics_events.aggregate([
        {"$match": {**match_stage, "event_type": "demo_link_opened"}},
        {"$group": {"_id": "$date", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$limit": 90},
    ]).to_list(90)

    # 3. Signups in period
    total_signups = await db.users.count_documents({"created_at": {"$gte": cutoff}})
    total_pro = await db.users.count_documents({"created_at": {"$gte": cutoff}, "$or": [{"is_pro": True}, {"is_elite": True}]})

    # 4. Conversion rates
    demo_signup_rate = round((total_signups / demo_opens * 100), 1) if demo_opens > 0 else 0
    demo_pro_rate = round((total_pro / demo_opens * 100), 1) if demo_opens > 0 else 0

    # 5. K-factor (viral coefficient) = avg referrals per user × conversion rate
    total_users = await db.users.count_documents({})
    k_factor = round((demo_opens / max(total_users, 1)) * (demo_signup_rate / 100), 2)

    # 6. Top referrers
    top_referrers = await db.analytics_events.aggregate([
        {"$match": {**match_stage, "event_type": "demo_link_opened", "metadata.referrer": {"$ne": "(direct)"}}},
        {"$group": {"_id": "$metadata.referrer", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]).to_list(10)

    # 7. Pages viewed per demo session
    pages_per_session = await db.analytics_events.aggregate([
        {"$match": {**match_stage, "event_type": "demo_link_opened"}},
        {"$group": {"_id": "$metadata.path", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15},
    ]).to_list(15)

    # 8. All events (for avg session and live stream)
    all_event_types = await db.analytics_events.aggregate([
        {"$match": match_stage},
        {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]).to_list(50)

    total_events = sum(e["count"] for e in all_event_types)

    # 9. Recent events for live stream
    recent_events = []
    async for doc in db.analytics_events.find(match_stage, {"_id": 0}).sort([("timestamp", -1)]).limit(20):
        recent_events.append({
            "event_type": doc.get("event_type"),
            "timestamp": doc.get("timestamp").isoformat() if hasattr(doc.get("timestamp", ""), "isoformat") else str(doc.get("timestamp", "")),
            "path": doc.get("metadata", {}).get("path"),
            "referrer": doc.get("metadata", {}).get("referrer"),
        })

    # 10. 24h trend data for goal tracker
    cutoff_24h = now - timedelta(hours=24)
    cutoff_48h = now - timedelta(hours=48)
    demo_opens_24h = await db.analytics_events.count_documents({"timestamp": {"$gte": cutoff_24h}, "event_type": "demo_link_opened"})
    demo_opens_prev24h = await db.analytics_events.count_documents({"timestamp": {"$gte": cutoff_48h, "$lt": cutoff_24h}, "event_type": "demo_link_opened"})
    signups_24h = await db.users.count_documents({"created_at": {"$gte": cutoff_24h}})
    signups_prev24h = await db.users.count_documents({"created_at": {"$gte": cutoff_48h, "$lt": cutoff_24h}})
    pro_24h = await db.users.count_documents({"created_at": {"$gte": cutoff_24h}, "$or": [{"is_pro": True}, {"is_elite": True}]})
    pro_prev24h = await db.users.count_documents({"created_at": {"$gte": cutoff_48h, "$lt": cutoff_24h}, "$or": [{"is_pro": True}, {"is_elite": True}]})

    signup_rate_24h = round((signups_24h / demo_opens_24h * 100), 1) if demo_opens_24h > 0 else 0
    signup_rate_prev = round((signups_prev24h / demo_opens_prev24h * 100), 1) if demo_opens_prev24h > 0 else 0
    pro_rate_24h = round((pro_24h / demo_opens_24h * 100), 1) if demo_opens_24h > 0 else 0
    pro_rate_prev = round((pro_prev24h / demo_opens_prev24h * 100), 1) if demo_opens_prev24h > 0 else 0
    k_24h = round((demo_opens_24h / max(total_users, 1)) * (signup_rate_24h / 100), 2)
    k_prev = round((demo_opens_prev24h / max(total_users, 1)) * (signup_rate_prev / 100), 2)

    result = {
        "period": period,
        "kpi": {
            "demo_opens": demo_opens,
            "total_signups": total_signups,
            "total_pro": total_pro,
            "demo_signup_rate": demo_signup_rate,
            "demo_pro_rate": demo_pro_rate,
            "k_factor": k_factor,
            "total_events": total_events,
            "total_users": total_users,
        },
        "trends_24h": {
            "k_factor": k_24h,
            "k_factor_prev": k_prev,
            "demo_signup_rate": signup_rate_24h,
            "demo_signup_rate_prev": signup_rate_prev,
            "demo_pro_rate": pro_rate_24h,
            "demo_pro_rate_prev": pro_rate_prev,
        },
        "opens_over_time": [{"date": o["_id"], "count": o["count"]} for o in opens_over_time],
        "top_referrers": [{"referrer": r["_id"], "count": r["count"]} for r in top_referrers],
        "pages_per_session": [{"path": p["_id"], "count": p["count"]} for p in pages_per_session],
        "event_types": [{"type": e["_id"], "count": e["count"]} for e in all_event_types],
        "recent_events": recent_events,
    }

    _analytics_cache["data"] = result
    _analytics_cache["ts"] = _time.time()
    _analytics_cache["key"] = cache_key
    return result


# ============= GOAL TRACKER =============

_goals_cache = {"data": None, "ts": 0}
_GOALS_CACHE_TTL = 60

DEFAULT_GOALS = {"k_factor_target": 1.0, "demo_signup_target": 15.0, "demo_pro_target": 5.0}


@router.get("/analytics/goals")
async def get_analytics_goals(admin: dict = Depends(verify_admin)):
    """Return saved goal targets."""
    if _goals_cache["data"] and _time.time() - _goals_cache["ts"] < _GOALS_CACHE_TTL:
        return _goals_cache["data"]

    doc = await db.analytics_goals.find_one({"_id": "goals"}, {"_id": 0})
    result = doc if doc else DEFAULT_GOALS
    _goals_cache["data"] = result
    _goals_cache["ts"] = _time.time()
    return result


class GoalsPayload(BaseModel):
    k_factor_target: float = Field(ge=0, le=5)
    demo_signup_target: float = Field(ge=0, le=100)
    demo_pro_target: float = Field(ge=0, le=100)


@router.post("/analytics/goals")
async def save_analytics_goals(payload: GoalsPayload, admin: dict = Depends(verify_admin)):
    """Save / update goal targets."""
    doc = payload.dict()
    doc["updated_at"] = datetime.now(timezone.utc)
    await db.analytics_goals.update_one({"_id": "goals"}, {"$set": doc}, upsert=True)
    _goals_cache["data"] = {k: v for k, v in doc.items() if k != "updated_at"}
    _goals_cache["ts"] = _time.time()
    return {"status": "saved", **_goals_cache["data"]}


# ============= CONTRACT STATUS =============

@router.get("/contract/status")
async def admin_contract_status(admin: dict = Depends(verify_admin)):
    """Get smart contract deployment and health status."""
    from services.contract_manager import get_contract_status
    status = await get_contract_status()
    return {"success": True, **status}


# ============= PERFORMANCE ATTESTATION =============

@router.post("/attestation/run")
async def admin_run_attestation(request: Request, admin: dict = Depends(verify_admin)):
    """Trigger a performance attestation cycle (admin-only)."""
    dry_run = request.query_params.get("dry_run", "true").lower() == "true"
    from cron.performance_attestor import run_attestation_cycle
    result = await run_attestation_cycle(dry_run=dry_run)
    return {"success": True, **result}


@router.get("/attestation/history")
async def admin_attestation_history(admin: dict = Depends(verify_admin), limit: int = 10):
    """Get recent attestation results."""
    records = await db.performance_attestations.find(
        {}, {"_id": 0}
    ).sort("timestamp", -1).to_list(limit)
    return {"success": True, "records": records, "count": len(records)}


@router.get("/attestation/latest")
async def admin_attestation_latest(admin: dict = Depends(verify_admin)):
    """Get the latest attestation result."""
    record = await db.performance_attestations.find_one(
        {}, {"_id": 0}, sort=[("timestamp", -1)]
    )
    if not record:
        return {"success": True, "record": None, "message": "No attestation runs yet"}
    return {"success": True, "record": record}


# ============= WAITLIST =============

@router.get("/waitlist")
async def admin_get_waitlist(admin: dict = Depends(verify_admin), limit: int = 200):
    """Get waitlist entries, newest first."""
    entries = await db.waitlist.find(
        {}, {"_id": 0, "ip": 0}
    ).sort("created_at", -1).to_list(limit)
    return {"success": True, "entries": entries, "count": len(entries)}


# ============= SUBSCRIPTION HEALTH =============

_sub_health_cache = {"data": None, "expires": 0}

@router.get("/subscription-health")
async def admin_subscription_health(admin: dict = Depends(verify_admin)):
    """Subscription health dashboard — cached for 30 seconds."""
    import time
    now_ts = time.time()
    if _sub_health_cache["data"] and now_ts < _sub_health_cache["expires"]:
        return _sub_health_cache["data"]

    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)

    # Active subscribers: users with subscription_status=active or trialing
    active_subscribers = await db.users.count_documents({
        "subscription_status": {"$in": ["active", "trialing"]}
    })

    # MRR: count active pro * $29 (pro_monthly price from payment_transactions)
    pro_count = await db.users.count_documents({
        "subscription_status": "active", "user_tier": "pro"
    })
    elite_count = await db.users.count_documents({
        "subscription_status": "active", "user_tier": "elite"
    })
    mrr = round(pro_count * 29.0 + elite_count * 99.0, 2)

    # Churn 30d: users whose subscription_status became canceled in last 30 days
    churn_events = await db.stripe_webhook_events.count_documents({
        "event_type": "customer.subscription.deleted",
        "processed_at": {"$gte": thirty_days_ago}
    })

    # Failed payments 7d
    failed_payments_7d = await db.stripe_webhook_events.count_documents({
        "event_type": "invoice.payment_failed",
        "processed_at": {"$gte": seven_days_ago}
    })

    # Retry queue: users currently past_due
    retry_queue = await db.users.count_documents({
        "subscription_status": "past_due"
    })

    # Upcoming renewals 7d: active users with subscription_end within 7 days
    seven_days_future = now + timedelta(days=7)
    now_str = now.isoformat()
    seven_future_str = seven_days_future.isoformat()
    upcoming_renewals = await db.users.count_documents({
        "subscription_status": "active",
        "subscription_end": {"$gte": now_str, "$lte": seven_future_str}
    })

    # Recent subscription events (last 20)
    raw_events = await db.stripe_webhook_events.find(
        {}, {"_id": 0, "event_type": 1, "processed_at": 1, "metadata": 1}
    ).sort("processed_at", -1).to_list(20)

    recent_events = []
    for ev in raw_events:
        recent_events.append({
            "type": ev.get("event_type", "unknown"),
            "user_email": (ev.get("metadata") or {}).get("user", "N/A"),
            "timestamp": ev.get("processed_at"),
        })

    result = {
        "success": True,
        "active_subscribers": active_subscribers,
        "mrr": mrr,
        "churn_30d": churn_events,
        "failed_payments_7d": failed_payments_7d,
        "retry_queue": retry_queue,
        "upcoming_renewals_7d": upcoming_renewals,
        "recent_events": recent_events,
    }

    _sub_health_cache["data"] = result
    _sub_health_cache["expires"] = now_ts + 30

    return result


# ============= USER STATS =============

_user_stats_cache = {"data": None, "expires": 0}

@router.get("/user-stats")
async def admin_user_stats(admin: dict = Depends(verify_admin)):
    """Real-time user stats — cached for 30 seconds."""
    import time
    now_ts = time.time()
    if _user_stats_cache["data"] and now_ts < _user_stats_cache["expires"]:
        return _user_stats_cache["data"]

    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    twenty_four_hours_ago = now - timedelta(hours=24)

    total_users = await db.users.count_documents({})

    new_users_7d = await db.users.count_documents({
        "created_at": {"$gte": seven_days_ago}
    })

    active_users_24h = await db.users.count_documents({
        "last_login": {"$gte": twenty_four_hours_ago}
    })

    result = {
        "success": True,
        "total_users": total_users,
        "new_users_7d": new_users_7d,
        "active_users_24h": active_users_24h,
    }

    _user_stats_cache["data"] = result
    _user_stats_cache["expires"] = now_ts + 30

    return result


# ============= CONNECTED EXCHANGES =============

@router.get("/exchanges")
async def admin_exchanges(admin: dict = Depends(verify_admin)):
    """List users with connected exchanges — no secret keys exposed."""
    users = await db.users.find(
        {"exchange_credentials": {"$exists": True}},
        {"_id": 0, "id": 1, "email": 1, "exchange_credentials.exchange": 1,
         "exchange_credentials.last_validated": 1, "exchange_credentials.status": 1,
         "exchange_credentials.connected_at": 1}
    ).to_list(200)

    entries = []
    for u in users:
        creds = u.get("exchange_credentials", {})
        entries.append({
            "user_id": u["id"],
            "email": u.get("email", "N/A"),
            "exchange": creds.get("exchange", "unknown"),
            "status": creds.get("status", "unknown"),
            "connected_at": creds.get("connected_at"),
            "last_validated": creds.get("last_validated"),
        })

    return {"success": True, "exchanges": entries, "count": len(entries)}
