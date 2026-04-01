"""
Strategy Marketplace Billing — Real Stripe Checkout + Webhooks + Subscription Sync
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid
import os
import logging

from database import db
from routes.auth import get_current_user
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest, CheckoutSessionResponse, CheckoutStatusResponse
)

logger = logging.getLogger("AlphaAI.Billing")
router = APIRouter(tags=["Billing"])

# Collections
strategies_col = db["strategies_mp"]
subscriptions_col = db["strategy_subscriptions"]
transactions_col = db["payment_transactions"]

# Fixed subscription pricing — server-side only, never from frontend
STRATEGY_SUBSCRIPTION_PRICE = 9.99  # USD/month
STRATEGY_SUBSCRIPTION_CURRENCY = "usd"

STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY")


def _get_stripe(request: Request) -> StripeCheckout:
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    return StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)


# ═══════════════════════════════════════════
#  Checkout
# ═══════════════════════════════════════════

class CheckoutRequest(BaseModel):
    origin_url: str = Field(..., description="Frontend origin (window.location.origin)")


@router.post("/api/marketplace/strategies/{strategy_id}/checkout")
async def create_checkout(strategy_id: str, body: CheckoutRequest, request: Request, user: dict = Depends(get_current_user)):
    """Create a Stripe Checkout session for strategy subscription."""
    strategy = await strategies_col.find_one({"id": strategy_id}, {"_id": 0})
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    if strategy["status"] != "published":
        raise HTTPException(status_code=400, detail="Cannot subscribe to an unpublished strategy")
    if strategy["creator_id"] == user["id"]:
        raise HTTPException(status_code=400, detail="Cannot subscribe to your own strategy")

    # Check existing active subscription
    existing = await subscriptions_col.find_one(
        {"strategy_id": strategy_id, "user_id": user["id"], "status": "active"}
    )
    if existing:
        raise HTTPException(status_code=409, detail="Already subscribed to this strategy")

    origin = body.origin_url.rstrip("/")
    success_url = f"{origin}/marketplace/{strategy_id}?session_id={{CHECKOUT_SESSION_ID}}&success=true"
    cancel_url = f"{origin}/marketplace/{strategy_id}?canceled=true"

    stripe = _get_stripe(request)

    metadata = {
        "type": "strategy_subscription",
        "strategy_id": strategy_id,
        "strategy_name": strategy["name"],
        "user_id": user["id"],
        "user_email": user.get("email", ""),
    }

    checkout_req = CheckoutSessionRequest(
        amount=STRATEGY_SUBSCRIPTION_PRICE,
        currency=STRATEGY_SUBSCRIPTION_CURRENCY,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata,
    )

    session: CheckoutSessionResponse = await stripe.create_checkout_session(checkout_req)

    # Create pending transaction record BEFORE redirect
    now = datetime.now(timezone.utc).isoformat()
    txn = {
        "id": str(uuid.uuid4()),
        "session_id": session.session_id,
        "user_id": user["id"],
        "user_email": user.get("email", ""),
        "strategy_id": strategy_id,
        "strategy_name": strategy["name"],
        "amount": STRATEGY_SUBSCRIPTION_PRICE,
        "currency": STRATEGY_SUBSCRIPTION_CURRENCY,
        "payment_status": "initiated",
        "status": "pending",
        "metadata": metadata,
        "created_at": now,
        "updated_at": now,
    }
    await transactions_col.insert_one(txn)

    return {"url": session.url, "session_id": session.session_id}


# ═══════════════════════════════════════════
#  Status Polling
# ═══════════════════════════════════════════

@router.get("/api/marketplace/checkout/status/{session_id}")
async def get_checkout_status(session_id: str, request: Request, user: dict = Depends(get_current_user)):
    """Poll Stripe for checkout session status and sync DB."""
    txn = await transactions_col.find_one({"session_id": session_id}, {"_id": 0})
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if txn["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not your transaction")

    # If already processed, return cached status
    if txn["payment_status"] in ("paid", "expired"):
        return {
            "payment_status": txn["payment_status"],
            "status": txn["status"],
            "strategy_id": txn["strategy_id"],
        }

    stripe = _get_stripe(request)
    status: CheckoutStatusResponse = await stripe.get_checkout_status(session_id)

    now = datetime.now(timezone.utc).isoformat()

    if status.payment_status == "paid" and txn["payment_status"] != "paid":
        # Update transaction
        await transactions_col.update_one(
            {"session_id": session_id},
            {"$set": {"payment_status": "paid", "status": "complete", "updated_at": now}}
        )
        # Create subscription entry (idempotent on session_id)
        existing_sub = await subscriptions_col.find_one({"stripe_session_id": session_id})
        if not existing_sub:
            sub = {
                "id": str(uuid.uuid4()),
                "strategy_id": txn["strategy_id"],
                "strategy_name": txn["strategy_name"],
                "user_id": txn["user_id"],
                "user_email": txn["user_email"],
                "creator_id": (await strategies_col.find_one({"id": txn["strategy_id"]}, {"_id": 0})).get("creator_id", ""),
                "status": "active",
                "stripe_session_id": session_id,
                "stripe_subscription_id": status.metadata.get("subscription_id"),
                "subscribed_at": now,
                "canceled_at": None,
            }
            await subscriptions_col.insert_one(sub)
            await strategies_col.update_one(
                {"id": txn["strategy_id"]}, {"$inc": {"subscriber_count": 1}}
            )
            logger.info(f"Subscription created via checkout: user={txn['user_id']}, strategy={txn['strategy_id']}")

    elif status.status == "expired":
        await transactions_col.update_one(
            {"session_id": session_id},
            {"$set": {"payment_status": "expired", "status": "expired", "updated_at": now}}
        )

    return {
        "payment_status": status.payment_status,
        "status": status.status,
        "strategy_id": txn["strategy_id"],
    }


# ═══════════════════════════════════════════
#  Stripe Webhook
# ═══════════════════════════════════════════

@router.post("/api/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    body = await request.body()
    sig = request.headers.get("Stripe-Signature", "")

    stripe = _get_stripe(request)

    try:
        event = await stripe.handle_webhook(body, sig)
    except Exception as e:
        logger.error(f"Webhook verification failed: {e}")
        raise HTTPException(status_code=400, detail="Webhook verification failed")

    now = datetime.now(timezone.utc).isoformat()
    event_type = event.event_type
    session_id = event.session_id

    logger.info(f"Stripe webhook: {event_type}, session={session_id}, status={event.payment_status}")

    if event.payment_status == "paid":
        # Update transaction
        await transactions_col.update_one(
            {"session_id": session_id},
            {"$set": {"payment_status": "paid", "status": "complete", "updated_at": now}}
        )

        # Create subscription (idempotent)
        txn = await transactions_col.find_one({"session_id": session_id}, {"_id": 0})
        if txn:
            existing_sub = await subscriptions_col.find_one({"stripe_session_id": session_id})
            if not existing_sub:
                strategy = await strategies_col.find_one({"id": txn["strategy_id"]}, {"_id": 0})
                sub = {
                    "id": str(uuid.uuid4()),
                    "strategy_id": txn["strategy_id"],
                    "strategy_name": txn["strategy_name"],
                    "user_id": txn["user_id"],
                    "user_email": txn["user_email"],
                    "creator_id": strategy.get("creator_id", "") if strategy else "",
                    "status": "active",
                    "stripe_session_id": session_id,
                    "stripe_subscription_id": event.metadata.get("subscription_id"),
                    "subscribed_at": now,
                    "canceled_at": None,
                }
                await subscriptions_col.insert_one(sub)
                await strategies_col.update_one(
                    {"id": txn["strategy_id"]}, {"$inc": {"subscriber_count": 1}}
                )

    elif event_type in ("checkout.session.expired",):
        await transactions_col.update_one(
            {"session_id": session_id},
            {"$set": {"payment_status": "expired", "status": "expired", "updated_at": now}}
        )

    return {"received": True}


# ═══════════════════════════════════════════
#  Unsubscribe (with Stripe cancellation)
# ═══════════════════════════════════════════

@router.post("/api/marketplace/strategies/{strategy_id}/cancel-subscription")
async def cancel_subscription(strategy_id: str, user: dict = Depends(get_current_user)):
    """Cancel a paid strategy subscription."""
    sub = await subscriptions_col.find_one(
        {"strategy_id": strategy_id, "user_id": user["id"], "status": "active"}
    )
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription found")

    now = datetime.now(timezone.utc).isoformat()

    await subscriptions_col.update_one(
        {"_id": sub["_id"]},
        {"$set": {"status": "canceled", "canceled_at": now}}
    )
    await strategies_col.update_one(
        {"id": strategy_id, "subscriber_count": {"$gt": 0}},
        {"$inc": {"subscriber_count": -1}}
    )

    return {"message": "Subscription canceled", "strategy_id": strategy_id}
