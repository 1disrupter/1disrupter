"""
Billing Portal — Self-serve subscription management for users.
Provides subscription overview, payment history, Stripe Billing Portal access.
"""
import os
import stripe
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import logging

from database import db
from routes.auth import get_current_user

logger = logging.getLogger("AlphaAI.Billing")
router = APIRouter(prefix="/api/billing", tags=["Billing Portal"])

subscriptions_col = db["strategy_subscriptions"]
transactions_col = db["payment_transactions"]
strategies_col = db["strategies_mp"]
users_col = db["users"]

# Stripe setup — uses Emergent proxy when sk_test_emergent key is detected
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY")


def _init_stripe():
    """Configure stripe SDK with the correct key and base URL."""
    stripe.api_key = STRIPE_API_KEY
    if STRIPE_API_KEY and "sk_test_emergent" in STRIPE_API_KEY:
        stripe.api_base = "https://integrations.emergentagent.com/stripe"


async def _get_or_create_stripe_customer(user: dict) -> str:
    """Get the user's Stripe customer ID, creating one if it doesn't exist or is invalid."""
    _init_stripe()
    user_doc = await users_col.find_one({"id": user["id"]}, {"_id": 0, "stripe_customer_id": 1, "email": 1, "name": 1})

    existing_id = user_doc.get("stripe_customer_id") if user_doc else None

    # Validate existing customer ID with Stripe
    if existing_id:
        try:
            stripe.Customer.retrieve(existing_id)
            return existing_id
        except Exception:
            logger.warning(f"Stale Stripe customer {existing_id} for user {user['id']}, creating new one")

    customer = stripe.Customer.create(
        email=user.get("email", ""),
        name=user.get("name", user.get("email", "")),
        metadata={"alphaai_user_id": user["id"]},
    )

    await users_col.update_one(
        {"id": user["id"]},
        {"$set": {"stripe_customer_id": customer.id, "updated_at": datetime.now(timezone.utc)}}
    )

    logger.info(f"Created Stripe customer {customer.id} for user {user['id']}")
    return customer.id


@router.get("/subscriptions")
async def get_user_subscriptions(user: dict = Depends(get_current_user)):
    """Get all subscriptions for the current user with strategy details."""
    subs = await subscriptions_col.find(
        {"user_id": user["id"]},
        {"_id": 0}
    ).sort("subscribed_at", -1).to_list(100)

    enriched = []
    for sub in subs:
        strategy = await strategies_col.find_one(
            {"id": sub.get("strategy_id")},
            {"_id": 0, "name": 1, "category": 1, "avg_rating": 1, "subscriber_count": 1, "status": 1}
        )
        enriched.append({
            "id": sub.get("id"),
            "strategy_id": sub.get("strategy_id"),
            "strategy_name": sub.get("strategy_name", "Unknown"),
            "status": sub.get("status", "unknown"),
            "subscribed_at": sub.get("subscribed_at"),
            "canceled_at": sub.get("canceled_at"),
            "stripe_session_id": sub.get("stripe_session_id"),
            "strategy": strategy,
        })

    active = [s for s in enriched if s["status"] == "active"]
    canceled = [s for s in enriched if s["status"] != "active"]

    return {
        "active_count": len(active),
        "total_count": len(enriched),
        "active": active,
        "canceled": canceled,
    }


@router.get("/payments")
async def get_payment_history(user: dict = Depends(get_current_user)):
    """Get payment transaction history for the current user."""
    txns = await transactions_col.find(
        {"user_id": user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)

    payments = []
    for txn in txns:
        payments.append({
            "id": txn.get("id"),
            "strategy_name": txn.get("strategy_name", "Unknown"),
            "amount": txn.get("amount", 0),
            "currency": txn.get("currency", "usd"),
            "payment_status": txn.get("payment_status", "unknown"),
            "status": txn.get("status", "unknown"),
            "created_at": txn.get("created_at"),
            "session_id": txn.get("session_id"),
        })

    return {"payments": payments, "count": len(payments)}


@router.get("/overview")
async def billing_overview(user: dict = Depends(get_current_user)):
    """Get billing overview: active subs count, total spent, next billing info."""
    active_subs = await subscriptions_col.count_documents(
        {"user_id": user["id"], "status": "active"}
    )

    # Calculate total spent from completed transactions
    pipeline = [
        {"$match": {"user_id": user["id"], "payment_status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
    ]
    agg = await transactions_col.aggregate(pipeline).to_list(1)
    total_spent = agg[0]["total"] if agg else 0
    total_payments = agg[0]["count"] if agg else 0

    monthly_cost = round(active_subs * 9.99, 2)

    return {
        "active_subscriptions": active_subs,
        "monthly_cost": monthly_cost,
        "total_spent": round(total_spent, 2),
        "total_payments": total_payments,
        "currency": "usd",
    }


class PortalRequest(BaseModel):
    return_url: str


@router.post("/portal")
async def create_billing_portal_session(body: PortalRequest, user: dict = Depends(get_current_user)):
    """Create a Stripe Billing Portal session for the authenticated user.
    The user can manage payment methods, view invoices, and cancel/reactivate subscriptions."""
    try:
        customer_id = await _get_or_create_stripe_customer(user)
    except Exception as e:
        logger.error(f"Failed to get/create Stripe customer for {user['id']}: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize billing customer")

    try:
        _init_stripe()
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=body.return_url,
        )
        return {"url": session.url}
    except Exception as e:
        logger.error(f"Stripe billing portal session creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create billing portal session")
