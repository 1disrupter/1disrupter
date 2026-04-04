"""
AlphaAI Referral System
- Unique referral links per user
- 20% recurring commission (tiered up to 30%)
- 7 days free for both referrer and referee
- Referral tracking and earnings dashboard
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
import secrets
import string
import logging

logger = logging.getLogger("AlphaAI.Referral")

# MongoDB connection
db = None

def init_db(database):
    global db
    db = database

router = APIRouter(prefix="/api/referrals", tags=["Referral System"])

# ============= CONFIGURATION =============

REFERRAL_CONFIG = {
    # Commission tiers (% of subscription revenue)
    "tiers": {
        "bronze": {"min_referrals": 0, "commission_rate": 0.20, "label": "Bronze", "color": "#CD7F32"},
        "silver": {"min_referrals": 6, "commission_rate": 0.25, "label": "Silver", "color": "#C0C0C0"},
        "gold": {"min_referrals": 16, "commission_rate": 0.30, "label": "Gold", "color": "#FFD700"},
        "platinum": {"min_referrals": 50, "commission_rate": 0.35, "label": "Platinum", "color": "#E5E4E2"}
    },
    # Free subscription days
    "referrer_free_days": 7,
    "referee_free_days": 7,
    # Payout settings
    "min_payout_amount": 25.00,
    "payout_methods": ["paypal", "crypto", "bank_transfer"],
    # Commission on subscription plans
    "commissionable_plans": {
        "pro_monthly": 29.00,
        "pro_yearly": 249.00,
        "elite_monthly": 99.00,
        "elite_yearly": 899.00
    }
}

# ============= MODELS =============

class ReferralCode(BaseModel):
    code: str
    user_id: str
    created_at: datetime
    total_clicks: int = 0
    total_signups: int = 0
    total_conversions: int = 0
    total_earnings: float = 0.0
    is_active: bool = True

class ReferralStats(BaseModel):
    referral_code: str
    referral_link: str
    tier: str
    tier_color: str
    commission_rate: float
    total_referrals: int
    pending_referrals: int
    converted_referrals: int
    total_earnings: float
    pending_earnings: float
    available_earnings: float
    free_days_earned: int
    next_tier: Optional[dict] = None

class ReferralActivity(BaseModel):
    id: str
    type: str  # "signup", "conversion", "commission", "payout"
    referee_email: Optional[str] = None
    amount: Optional[float] = None
    plan: Optional[str] = None
    status: str
    timestamp: datetime

class PayoutRequest(BaseModel):
    amount: float = Field(..., ge=25.0)
    method: str  # "paypal", "crypto", "bank_transfer"
    details: dict  # Payment details (email, wallet, etc.)

class CreateReferralResponse(BaseModel):
    code: str
    link: str
    message: str

# ============= HELPER FUNCTIONS =============

def generate_referral_code(length: int = 8) -> str:
    """Generate a unique, memorable referral code"""
    # Use alphanumeric without confusing characters (0, O, l, 1, I)
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(secrets.choice(chars) for _ in range(length))

def get_tier_for_referrals(num_referrals: int) -> dict:
    """Determine tier based on number of successful referrals"""
    tiers = REFERRAL_CONFIG["tiers"]
    current_tier = tiers["bronze"]
    
    for tier_name, tier_data in sorted(tiers.items(), key=lambda x: x[1]["min_referrals"], reverse=True):
        if num_referrals >= tier_data["min_referrals"]:
            current_tier = {**tier_data, "name": tier_name}
            break
    
    return current_tier

def get_next_tier(num_referrals: int) -> Optional[dict]:
    """Get the next tier and referrals needed"""
    tiers = REFERRAL_CONFIG["tiers"]
    
    for tier_name, tier_data in sorted(tiers.items(), key=lambda x: x[1]["min_referrals"]):
        if num_referrals < tier_data["min_referrals"]:
            return {
                "name": tier_name,
                "label": tier_data["label"],
                "commission_rate": tier_data["commission_rate"],
                "referrals_needed": tier_data["min_referrals"] - num_referrals
            }
    
    return None  # Already at highest tier

def mask_email(email: str) -> str:
    """Mask email for privacy: john@example.com -> j***@e***.com"""
    parts = email.split('@')
    if len(parts) != 2:
        return "***@***.***"
    
    local = parts[0]
    domain = parts[1].split('.')
    
    masked_local = local[0] + '***' if len(local) > 0 else '***'
    masked_domain = domain[0][0] + '***' if len(domain) > 0 and len(domain[0]) > 0 else '***'
    
    return f"{masked_local}@{masked_domain}.{''.join(domain[1:]) if len(domain) > 1 else 'com'}"

async def get_current_user_from_token(request: Request) -> dict:
    """Get current user from JWT token"""
    from routes.auth import get_current_user
    return await get_current_user(request)

# ============= API ROUTES =============

@router.post("/create-code", response_model=CreateReferralResponse)
async def create_referral_code(request: Request):
    """Create or get existing referral code for user"""
    user = await get_current_user_from_token(request)
    user_id = user["id"]
    
    # Check if user already has a code
    existing = await db.referral_codes.find_one({"user_id": user_id}, {"_id": 0})
    
    if existing:
        base_url = os.environ.get("APP_URL", "https://alphaai.com")
        return CreateReferralResponse(
            code=existing["code"],
            link=f"{base_url}/register?ref={existing['code']}",
            message="Referral code retrieved"
        )
    
    # Generate unique code
    code = generate_referral_code()
    while await db.referral_codes.find_one({"code": code}):
        code = generate_referral_code()
    
    # Create referral code record
    now = datetime.now(timezone.utc)
    referral_code = {
        "code": code,
        "user_id": user_id,
        "user_email": user["email"],
        "created_at": now,
        "total_clicks": 0,
        "total_signups": 0,
        "total_conversions": 0,
        "total_earnings": 0.0,
        "pending_earnings": 0.0,
        "available_earnings": 0.0,
        "free_days_earned": 0,
        "is_active": True
    }
    
    await db.referral_codes.insert_one(referral_code)
    
    base_url = os.environ.get("APP_URL", "https://alphaai.com")
    logger.info(f"Referral code created: {code} for user {user['email']}")
    
    return CreateReferralResponse(
        code=code,
        link=f"{base_url}/register?ref={code}",
        message="Referral code created successfully"
    )

@router.get("/stats", response_model=ReferralStats)
async def get_referral_stats(request: Request):
    """Get referral statistics for current user"""
    user = await get_current_user_from_token(request)
    user_id = user["id"]
    
    # Get referral code
    ref_code = await db.referral_codes.find_one({"user_id": user_id}, {"_id": 0})
    
    if not ref_code:
        # Create one if doesn't exist
        create_response = await create_referral_code(request)
        ref_code = await db.referral_codes.find_one({"user_id": user_id}, {"_id": 0})
    
    # Count referrals by status
    pending = await db.referrals.count_documents({
        "referrer_id": user_id,
        "status": "pending"
    })
    
    converted = await db.referrals.count_documents({
        "referrer_id": user_id,
        "status": "converted"
    })
    
    total = ref_code.get("total_signups", 0)
    
    # Determine tier
    tier = get_tier_for_referrals(converted)
    next_tier = get_next_tier(converted)
    
    base_url = os.environ.get("APP_URL", "https://alphaai.com")
    
    return ReferralStats(
        referral_code=ref_code["code"],
        referral_link=f"{base_url}/register?ref={ref_code['code']}",
        tier=tier["label"],
        tier_color=tier["color"],
        commission_rate=tier["commission_rate"],
        total_referrals=total,
        pending_referrals=pending,
        converted_referrals=converted,
        total_earnings=ref_code.get("total_earnings", 0.0),
        pending_earnings=ref_code.get("pending_earnings", 0.0),
        available_earnings=ref_code.get("available_earnings", 0.0),
        free_days_earned=ref_code.get("free_days_earned", 0),
        next_tier=next_tier
    )

@router.get("/activity")
async def get_referral_activity(
    request: Request,
    limit: int = Query(20, le=100),
    offset: int = Query(0)
):
    """Get referral activity history"""
    user = await get_current_user_from_token(request)
    user_id = user["id"]
    
    # Get activity from referrals collection
    referrals = await db.referrals.find(
        {"referrer_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
    
    # Get payouts
    payouts = await db.referral_payouts.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    # Format activity
    activity = []
    
    for ref in referrals:
        activity.append({
            "id": ref.get("id", ""),
            "type": "conversion" if ref.get("status") == "converted" else "signup",
            "referee_email": mask_email(ref.get("referee_email", "")),
            "amount": ref.get("commission_amount"),
            "plan": ref.get("converted_plan"),
            "status": ref.get("status", "pending"),
            "timestamp": ref.get("created_at", datetime.now(timezone.utc))
        })
    
    for payout in payouts:
        activity.append({
            "id": payout.get("id", ""),
            "type": "payout",
            "referee_email": None,
            "amount": payout.get("amount"),
            "plan": None,
            "status": payout.get("status", "pending"),
            "timestamp": payout.get("created_at", datetime.now(timezone.utc))
        })
    
    # Sort by timestamp
    activity.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "activity": activity[:limit],
        "total": len(activity)
    }

@router.get("/earnings")
async def get_earnings_breakdown(request: Request):
    """Get detailed earnings breakdown"""
    user = await get_current_user_from_token(request)
    user_id = user["id"]
    
    ref_code = await db.referral_codes.find_one({"user_id": user_id}, {"_id": 0})
    
    if not ref_code:
        return {
            "total_earnings": 0,
            "pending_earnings": 0,
            "available_earnings": 0,
            "paid_out": 0,
            "monthly_breakdown": [],
            "by_plan": {}
        }
    
    # Get all converted referrals with commissions
    referrals = await db.referrals.find(
        {"referrer_id": user_id, "status": "converted"},
        {"_id": 0}
    ).to_list(1000)
    
    # Monthly breakdown
    monthly = {}
    by_plan = {}
    
    for ref in referrals:
        month = ref.get("converted_at", ref.get("created_at", datetime.now(timezone.utc))).strftime("%Y-%m")
        plan = ref.get("converted_plan", "unknown")
        amount = ref.get("commission_amount", 0)
        
        monthly[month] = monthly.get(month, 0) + amount
        by_plan[plan] = by_plan.get(plan, 0) + amount
    
    # Get total paid out
    paid_pipeline = [
        {"$match": {"user_id": user_id, "status": "completed"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    paid_result = await db.referral_payouts.aggregate(paid_pipeline).to_list(1)
    paid_out = paid_result[0]["total"] if paid_result else 0
    
    return {
        "total_earnings": ref_code.get("total_earnings", 0),
        "pending_earnings": ref_code.get("pending_earnings", 0),
        "available_earnings": ref_code.get("available_earnings", 0),
        "paid_out": paid_out,
        "monthly_breakdown": [{"month": k, "amount": v} for k, v in sorted(monthly.items())],
        "by_plan": by_plan
    }

@router.post("/request-payout")
async def request_payout(payout: PayoutRequest, request: Request):
    """Request a payout of available earnings"""
    user = await get_current_user_from_token(request)
    user_id = user["id"]
    
    # Validate payout method
    if payout.method not in REFERRAL_CONFIG["payout_methods"]:
        raise HTTPException(status_code=400, detail=f"Invalid payout method. Choose from: {REFERRAL_CONFIG['payout_methods']}")
    
    # Get available earnings
    ref_code = await db.referral_codes.find_one({"user_id": user_id}, {"_id": 0})
    
    if not ref_code:
        raise HTTPException(status_code=400, detail="No referral account found")
    
    available = ref_code.get("available_earnings", 0)
    
    if payout.amount > available:
        raise HTTPException(status_code=400, detail=f"Insufficient balance. Available: ${available:.2f}")
    
    if payout.amount < REFERRAL_CONFIG["min_payout_amount"]:
        raise HTTPException(status_code=400, detail=f"Minimum payout is ${REFERRAL_CONFIG['min_payout_amount']}")
    
    # Create payout request
    now = datetime.now(timezone.utc)
    payout_record = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "user_email": user["email"],
        "amount": payout.amount,
        "method": payout.method,
        "details": payout.details,
        "status": "pending",
        "created_at": now,
        "processed_at": None
    }
    
    await db.referral_payouts.insert_one(payout_record)
    
    # Deduct from available earnings
    await db.referral_codes.update_one(
        {"user_id": user_id},
        {"$inc": {"available_earnings": -payout.amount}}
    )
    
    logger.info(f"Payout requested: ${payout.amount} by {user['email']} via {payout.method}")
    
    return {
        "success": True,
        "message": f"Payout request for ${payout.amount:.2f} submitted",
        "payout_id": payout_record["id"],
        "status": "pending",
        "estimated_processing": "3-5 business days"
    }

@router.get("/leaderboard")
async def get_referral_leaderboard(limit: int = Query(10, le=50)):
    """Get top referrers leaderboard"""
    pipeline = [
        {"$match": {"is_active": True}},
        {"$project": {
            "_id": 0,
            "user_email": 1,
            "total_conversions": 1,
            "total_earnings": 1
        }},
        {"$sort": {"total_conversions": -1}},
        {"$limit": limit}
    ]
    
    top_referrers = await db.referral_codes.aggregate(pipeline).to_list(limit)
    
    leaderboard = []
    for i, ref in enumerate(top_referrers):
        tier = get_tier_for_referrals(ref.get("total_conversions", 0))
        leaderboard.append({
            "rank": i + 1,
            "email": mask_email(ref.get("user_email", "")),
            "referrals": ref.get("total_conversions", 0),
            "tier": tier["label"],
            "tier_color": tier["color"]
        })
    
    return {"leaderboard": leaderboard}

# ============= TRACKING ENDPOINTS (called by other services) =============

@router.post("/track-click")
async def track_referral_click(code: str = Query(...)):
    """Track when someone clicks a referral link"""
    ref_code = await db.referral_codes.find_one({"code": code.upper()})
    
    if not ref_code:
        return {"tracked": False, "reason": "Invalid code"}
    
    await db.referral_codes.update_one(
        {"code": code.upper()},
        {"$inc": {"total_clicks": 1}}
    )
    
    return {"tracked": True}

@router.post("/track-signup")
async def track_referral_signup(
    code: str = Query(...),
    referee_id: str = Query(...),
    referee_email: str = Query(...)
):
    """Track when a referred user signs up"""
    ref_code = await db.referral_codes.find_one({"code": code.upper()}, {"_id": 0})
    
    if not ref_code:
        return {"tracked": False, "reason": "Invalid code"}
    
    # Check if this user was already referred
    existing = await db.referrals.find_one({"referee_id": referee_id})
    if existing:
        return {"tracked": False, "reason": "User already referred"}
    
    now = datetime.now(timezone.utc)
    
    # Create referral record
    referral = {
        "id": str(uuid.uuid4()),
        "referrer_id": ref_code["user_id"],
        "referrer_code": code.upper(),
        "referee_id": referee_id,
        "referee_email": referee_email,
        "status": "pending",  # pending -> converted
        "created_at": now,
        "converted_at": None,
        "converted_plan": None,
        "commission_amount": 0,
        "commission_paid": False
    }
    
    await db.referrals.insert_one(referral)
    
    # Update referral code stats
    await db.referral_codes.update_one(
        {"code": code.upper()},
        {"$inc": {"total_signups": 1}}
    )
    
    # Grant free days to referee
    free_days = REFERRAL_CONFIG["referee_free_days"]
    await db.users.update_one(
        {"id": referee_id},
        {
            "$set": {
                "referred_by": code.upper(),
                "referral_bonus_days": free_days,
                "referral_bonus_expires": now + timedelta(days=free_days)
            }
        }
    )
    
    logger.info(f"Referral signup tracked: {referee_email} via {code}")
    
    return {
        "tracked": True,
        "referee_bonus_days": free_days,
        "message": f"Welcome! You've received {free_days} days of free Pro access"
    }

@router.post("/track-conversion")
async def track_referral_conversion(
    referee_id: str = Query(...),
    plan: str = Query(...),
    amount: float = Query(...)
):
    """Track when a referred user converts to paid"""
    # Find the referral
    referral = await db.referrals.find_one({"referee_id": referee_id}, {"_id": 0})
    
    if not referral:
        return {"tracked": False, "reason": "No referral found"}
    
    if referral.get("status") == "converted":
        # Handle recurring commission
        pass
    
    # Get referrer's tier
    ref_code = await db.referral_codes.find_one(
        {"user_id": referral["referrer_id"]},
        {"_id": 0}
    )
    
    conversions = ref_code.get("total_conversions", 0)
    tier = get_tier_for_referrals(conversions)
    commission_rate = tier["commission_rate"]
    commission_amount = amount * commission_rate
    
    now = datetime.now(timezone.utc)
    
    # Update referral record
    await db.referrals.update_one(
        {"referee_id": referee_id},
        {
            "$set": {
                "status": "converted",
                "converted_at": now,
                "converted_plan": plan,
                "commission_rate": commission_rate,
                "commission_amount": commission_amount
            }
        }
    )
    
    # Update referrer stats
    await db.referral_codes.update_one(
        {"user_id": referral["referrer_id"]},
        {
            "$inc": {
                "total_conversions": 1,
                "total_earnings": commission_amount,
                "pending_earnings": commission_amount,
                "free_days_earned": REFERRAL_CONFIG["referrer_free_days"]
            }
        }
    )
    
    # Grant free days to referrer
    await db.users.update_one(
        {"id": referral["referrer_id"]},
        {
            "$inc": {"bonus_pro_days": REFERRAL_CONFIG["referrer_free_days"]}
        }
    )
    
    logger.info(f"Referral conversion: {plan} - ${commission_amount:.2f} commission to {referral['referrer_id']}")
    
    return {
        "tracked": True,
        "commission_amount": commission_amount,
        "commission_rate": commission_rate,
        "referrer_bonus_days": REFERRAL_CONFIG["referrer_free_days"]
    }

@router.get("/validate-code")
async def validate_referral_code(code: str = Query(...)):
    """Validate a referral code (public endpoint)"""
    ref_code = await db.referral_codes.find_one(
        {"code": code.upper(), "is_active": True},
        {"_id": 0, "user_email": 1, "code": 1}
    )
    
    if not ref_code:
        return {"valid": False}
    
    return {
        "valid": True,
        "code": ref_code["code"],
        "referrer": mask_email(ref_code.get("user_email", "")),
        "bonus": f"{REFERRAL_CONFIG['referee_free_days']} days free Pro access"
    }

@router.get("/config")
async def get_referral_config():
    """Get public referral program configuration"""
    return {
        "tiers": [
            {
                "name": data["label"],
                "color": data["color"],
                "min_referrals": data["min_referrals"],
                "commission_rate": f"{int(data['commission_rate'] * 100)}%"
            }
            for name, data in sorted(
                REFERRAL_CONFIG["tiers"].items(),
                key=lambda x: x[1]["min_referrals"]
            )
        ],
        "referrer_bonus": f"{REFERRAL_CONFIG['referrer_free_days']} days free Pro",
        "referee_bonus": f"{REFERRAL_CONFIG['referee_free_days']} days free Pro",
        "min_payout": f"${REFERRAL_CONFIG['min_payout_amount']}",
        "payout_methods": REFERRAL_CONFIG["payout_methods"]
    }


# ============= VALIDATE BY REF PARAM (code OR user ID) =============

@router.get("/validate/{ref_param}")
async def validate_referral_param(ref_param: str):
    """Validate a referral from ?ref= URL param. Accepts referral code OR user ID."""
    # Try as referral code first
    ref_code = await db.referral_codes.find_one(
        {"code": ref_param.upper(), "is_active": True},
        {"_id": 0, "user_id": 1, "user_email": 1, "code": 1}
    )
    if ref_code:
        return {
            "valid": True,
            "referral_code": ref_code["code"],
            "referrer_id": ref_code["user_id"],
            "referrer_name": mask_email(ref_code.get("user_email", "")),
            "bonus": f"{REFERRAL_CONFIG['referee_free_days']} days free Pro access",
        }

    # Try as user ID
    user = await db.users.find_one({"id": ref_param}, {"_id": 0, "id": 1, "email": 1, "name": 1})
    if user:
        # Auto-create referral code for this user if not exists
        existing = await db.referral_codes.find_one({"user_id": user["id"]}, {"_id": 0})
        if not existing:
            code = generate_referral_code()
            while await db.referral_codes.find_one({"code": code}):
                code = generate_referral_code()
            await db.referral_codes.insert_one({
                "code": code,
                "user_id": user["id"],
                "user_email": user.get("email", ""),
                "created_at": datetime.now(timezone.utc),
                "total_clicks": 0,
                "total_signups": 0,
                "total_conversions": 0,
                "total_earnings": 0.0,
                "pending_earnings": 0.0,
                "available_earnings": 0.0,
                "free_days_earned": 0,
                "is_active": True,
            })
            existing = await db.referral_codes.find_one({"user_id": user["id"]}, {"_id": 0})

        return {
            "valid": True,
            "referral_code": existing["code"],
            "referrer_id": user["id"],
            "referrer_name": user.get("name") or mask_email(user.get("email", "")),
            "bonus": f"{REFERRAL_CONFIG['referee_free_days']} days free Pro access",
        }

    return {"valid": False}


# ============= ADMIN REFERRAL ANALYTICS =============

@router.get("/admin/summary")
async def admin_referral_summary(admin_key: str = Query(...)):
    """Admin-only: Referral program summary."""
    if admin_key != os.environ.get("ADMIN_SECRET", "alphaai_admin_2026"):
        raise HTTPException(status_code=403, detail="Admin access denied")

    total_referrals = await db.referrals.count_documents({})
    total_converted = await db.referrals.count_documents({"status": "converted"})
    total_pending = await db.referrals.count_documents({"status": "pending"})

    # Revenue from referred users
    pipeline = [
        {"$match": {"status": "converted"}},
        {"$group": {"_id": None, "total": {"$sum": "$commission_amount"}}}
    ]
    earnings_agg = await db.referrals.aggregate(pipeline).to_list(1)
    total_commissions = earnings_agg[0]["total"] if earnings_agg else 0

    # Active subscribers from referrals
    referred_ids = [r["referee_id"] async for r in db.referrals.find({}, {"_id": 0, "referee_id": 1})]
    active_subs_from_referrals = 0
    if referred_ids:
        active_subs_from_referrals = await db.strategy_subscriptions.count_documents(
            {"user_id": {"$in": referred_ids}, "status": "active"}
        )

    revenue_from_referrals = round(active_subs_from_referrals * 9.99, 2)

    # Top referrers
    top_pipeline = [
        {"$match": {"is_active": True, "total_signups": {"$gt": 0}}},
        {"$sort": {"total_conversions": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "user_id": 1, "user_email": 1, "code": 1, "total_signups": 1, "total_conversions": 1, "total_earnings": 1}},
    ]
    top_referrers = await db.referral_codes.aggregate(top_pipeline).to_list(10)

    return {
        "total_referrals": total_referrals,
        "total_converted": total_converted,
        "total_pending": total_pending,
        "active_subscribers_from_referrals": active_subs_from_referrals,
        "total_revenue_from_referrals": revenue_from_referrals,
        "total_commissions_owed": round(total_commissions, 2),
        "top_referrers": [
            {
                "email": mask_email(r.get("user_email", "")),
                "code": r.get("code"),
                "signups": r.get("total_signups", 0),
                "conversions": r.get("total_conversions", 0),
                "earnings": r.get("total_earnings", 0),
            }
            for r in top_referrers
        ],
    }


@router.get("/admin/events")
async def admin_referral_events(
    admin_key: str = Query(...),
    time_range: str = Query("7d", alias="range", regex="^(today|7d|30d)$"),
):
    """Admin-only: Referral events over time for charts."""
    if admin_key != os.environ.get("ADMIN_SECRET", "alphaai_admin_2026"):
        raise HTTPException(status_code=403, detail="Admin access denied")

    now = datetime.now(timezone.utc)
    if time_range == "today":
        cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_range == "7d":
        cutoff = now - timedelta(days=7)
    else:
        cutoff = now - timedelta(days=30)

    signups = await db.referrals.count_documents({"created_at": {"$gte": cutoff}})
    conversions = await db.referrals.count_documents({"converted_at": {"$gte": cutoff}})

    # Daily breakdown
    days = {"today": 1, "7d": 7, "30d": 30}[time_range]
    dates = [(now - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days - 1, -1, -1)]

    # Signup daily
    signup_pipeline = [
        {"$match": {"created_at": {"$gte": cutoff}}},
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}, "count": {"$sum": 1}}},
    ]
    signup_agg = {d["_id"]: d["count"] async for d in db.referrals.aggregate(signup_pipeline)}

    # Conversion daily
    conv_pipeline = [
        {"$match": {"converted_at": {"$gte": cutoff, "$ne": None}}},
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$converted_at"}}, "count": {"$sum": 1}}},
    ]
    conv_agg = {d["_id"]: d["count"] async for d in db.referrals.aggregate(conv_pipeline)}

    daily = [
        {"date": d, "signups": signup_agg.get(d, 0), "conversions": conv_agg.get(d, 0)}
        for d in dates
    ]

    return {
        "range": time_range,
        "totals": {"signups": signups, "conversions": conversions},
        "daily": daily,
    }
