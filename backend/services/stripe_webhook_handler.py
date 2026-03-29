"""
AlphaAI Stripe Webhook Handler
Comprehensive handler for all Stripe subscription lifecycle events.
Manages state transitions, admin broadcasting, founder alerts, and idempotency.
"""
import os
import asyncio
import logging
import stripe
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("AlphaAI.StripeWebhook")

db = None
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

def init_db(database):
    global db
    db = database


# ── Subscription Status Constants ──────────────────────────────

STATUS_ACTIVE = "active"
STATUS_TRIALING = "trialing"
STATUS_PAST_DUE = "past_due"
STATUS_CANCELED = "canceled"
STATUS_FLAGGED = "flagged"

HANDLED_EVENTS = {
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "invoice.payment_succeeded",
    "invoice.payment_failed",
    "customer.subscription.trial_will_end",
    "charge.refunded",
    "charge.dispute.created",
}


# ── Signature Verification ─────────────────────────────────────

def verify_stripe_signature(payload: bytes, sig_header: str) -> dict:
    """Verify Stripe webhook signature and return parsed event."""
    if STRIPE_WEBHOOK_SECRET:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        return event
    # No secret configured — parse raw (test mode)
    import json
    return json.loads(payload)


# ── Idempotency ────────────────────────────────────────────────

async def is_event_processed(event_id: str) -> bool:
    if not event_id:
        return False
    existing = await db.stripe_webhook_events.find_one({"event_id": event_id})
    return existing is not None


async def mark_event_processed(event_id: str, event_type: str, metadata: dict = None):
    await db.stripe_webhook_events.insert_one({
        "event_id": event_id,
        "event_type": event_type,
        "processed_at": datetime.now(timezone.utc),
        "metadata": metadata or {},
    })


# ── User Lookup Helpers ────────────────────────────────────────

async def find_user_by_stripe_customer(customer_id: str):
    """Find user by stripe_customer_id."""
    if not customer_id:
        return None
    user = await db.users.find_one({"stripe_customer_id": customer_id}, {"_id": 0})
    return user


async def find_user_by_email(email: str):
    if not email:
        return None
    user = await db.users.find_one({"email": email}, {"_id": 0})
    return user


async def find_user_by_session(session_id: str):
    """Find user via payment_transactions → email or wallet."""
    tx = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if not tx:
        return None, tx
    email = tx.get("metadata", {}).get("user_email")
    if email:
        user = await find_user_by_email(email)
        if user:
            return user, tx
    wallet = tx.get("wallet_address")
    if wallet and wallet != "demo_user":
        investor = await db.investors.find_one({"wallet_address": wallet}, {"_id": 0})
        if investor:
            return investor, tx
    return None, tx


# ── State Transition ───────────────────────────────────────────

async def update_subscription_status(
    user_id: str,
    email: str,
    status: str,
    tier: str = None,
    period_end: datetime = None,
    stripe_customer_id: str = None,
    stripe_subscription_id: str = None,
    reason: str = None,
):
    """Update subscription state on both users and investors collections."""
    now = datetime.now(timezone.utc)
    user_update = {
        "subscription_status": status,
        "subscription_updated_at": now,
    }
    if tier:
        user_update["user_tier"] = tier
        user_update["is_pro"] = tier in ("pro", "elite")
        user_update["is_elite"] = tier == "elite"
    if period_end:
        user_update["subscription_end"] = period_end
    if stripe_customer_id:
        user_update["stripe_customer_id"] = stripe_customer_id
    if stripe_subscription_id:
        user_update["stripe_subscription_id"] = stripe_subscription_id
    if status == STATUS_ACTIVE:
        user_update["pro_since"] = now
    if status == STATUS_CANCELED:
        user_update["user_tier"] = tier or "free"
        user_update["is_pro"] = False
        user_update["is_elite"] = False

    # Update users collection
    if email:
        await db.users.update_one({"email": email}, {"$set": user_update})

    # Update investors collection
    if user_id:
        investor_update = {
            "is_pro": user_update.get("is_pro", False),
            "is_elite": user_update.get("is_elite", False),
        }
        if status == STATUS_ACTIVE:
            investor_update["pro_since"] = now
        await db.investors.update_one(
            {"wallet_address": user_id},
            {"$set": investor_update},
        )

    logger.info(f"Subscription state → {status} for user={email or user_id} reason={reason}")


# ── Traffic Event Logging ──────────────────────────────────────

async def log_stripe_event(event_type: str, stripe_event_id: str, user_id: str = None, metadata: dict = None):
    doc = {
        "type": "stripe_event",
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc),
        "metadata": {
            "stripe_event_type": event_type,
            "stripe_event_id": stripe_event_id,
            **(metadata or {}),
        },
    }
    try:
        await db.traffic_events.insert_one(doc)
    except Exception as e:
        logger.error(f"Failed to log stripe event: {e}")


# ── Admin Broadcast ────────────────────────────────────────────

async def broadcast_admin_event(event_type: str, user_id: str = None, stripe_event_id: str = None, metadata: dict = None):
    from services.admin_events_manager import admin_events_manager

    payload = {
        "id": f"stripe-{stripe_event_id or 'unknown'}",
        "type": event_type,
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "stripe_event_id": stripe_event_id,
            **(metadata or {}),
        },
    }
    try:
        await admin_events_manager.broadcast_event(payload)
    except Exception as e:
        logger.error(f"Failed to broadcast admin event: {e}")


# ── Founder Email Alert ────────────────────────────────────────

async def send_founder_stripe_alert(
    event_type: str,
    stripe_event_id: str,
    user_id: str = None,
    error_details: str = None,
    is_demo: bool = False,
):
    if is_demo:
        logger.info(f"Demo mode: founder alert suppressed for stripe {event_type}")
        return

    founder_email = os.environ.get("FOUNDER_ALERT_EMAIL", "")
    if not founder_email:
        logger.info("FOUNDER_ALERT_EMAIL not set, skipping stripe alert email")
        return

    try:
        from services.email_service import send_email
    except ImportError:
        logger.error("email_service not available for founder alert")
        return

    now = datetime.now(timezone.utc)
    subject = f"[AlphaAI ALERT] Stripe Webhook Issue — {event_type}"
    html = f"""
    <div style="font-family: -apple-system, sans-serif; max-width: 600px; margin: 0 auto; background: #0a0a0a; color: #e4e4e7; padding: 32px; border-radius: 12px;">
      <div style="border-left: 4px solid #ef4444; padding-left: 16px; margin-bottom: 24px;">
        <h2 style="color: #ef4444; margin: 0 0 4px 0; font-size: 18px;">Stripe Webhook Alert</h2>
        <p style="color: #a1a1aa; margin: 0; font-size: 13px;">{now.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
      </div>
      <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
        <tr><td style="padding: 8px; color: #a1a1aa; font-size: 12px;">Event Type</td><td style="padding: 8px; font-weight: bold; font-size: 14px; color: #ef4444;">{event_type}</td></tr>
        <tr><td style="padding: 8px; color: #a1a1aa; font-size: 12px;">User ID</td><td style="padding: 8px; font-size: 14px;">{user_id or 'Unknown'}</td></tr>
        <tr><td style="padding: 8px; color: #a1a1aa; font-size: 12px;">Stripe Event ID</td><td style="padding: 8px; font-size: 14px; font-family: monospace;">{stripe_event_id or 'N/A'}</td></tr>
        <tr><td style="padding: 8px; color: #a1a1aa; font-size: 12px;">Error Details</td><td style="padding: 8px; font-size: 14px; color: #fbbf24;">{error_details or 'N/A'}</td></tr>
      </table>
      <hr style="border: none; border-top: 1px solid #27272a; margin: 24px 0;" />
      <p style="color: #52525b; font-size: 11px;">AlphaAI Stripe Monitoring — <a href='{os.environ.get("APP_URL", "")}/admin/traffic' style='color: #7B61FF;'>View Dashboard</a></p>
    </div>
    """

    for attempt in range(3):
        try:
            result = await send_email(founder_email, subject, html)
            if result.get("status") in ("sent", "logged"):
                logger.info(f"Founder stripe alert sent for {event_type}")
                return
        except Exception as e:
            logger.error(f"Founder stripe email attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                await asyncio.sleep(1)

    logger.error(f"Failed to send founder stripe alert for {event_type} after 3 attempts")


# ── Event Handlers ─────────────────────────────────────────────

async def handle_checkout_session_completed(event_data: dict, stripe_event_id: str):
    """checkout.session.completed → activate subscription"""
    session_id = event_data.get("id")
    customer_id = event_data.get("customer")
    customer_email = event_data.get("customer_details", {}).get("email") or event_data.get("customer_email")
    subscription_id = event_data.get("subscription")

    user, tx = await find_user_by_session(session_id)
    email = customer_email or (tx or {}).get("metadata", {}).get("user_email")
    wallet = (tx or {}).get("wallet_address")
    pkg_id = (tx or {}).get("package_id", "pro_monthly")
    from routes.payments import PRO_SUBSCRIPTION_PACKAGES
    pkg = PRO_SUBSCRIPTION_PACKAGES.get(pkg_id, {})
    tier = pkg.get("tier", "pro")

    await update_subscription_status(
        user_id=wallet,
        email=email,
        status=STATUS_ACTIVE,
        tier=tier,
        stripe_customer_id=customer_id,
        stripe_subscription_id=subscription_id,
        reason="checkout_completed",
    )

    # Update transaction record
    if session_id:
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {
                "payment_status": "paid",
                "status": "checkout.session.completed",
                "pro_activated_at": datetime.now(timezone.utc),
                "webhook_event_id": stripe_event_id,
                "updated_at": datetime.now(timezone.utc),
            }}
        )

    await broadcast_admin_event("subscription_activated", user_id=email or wallet, stripe_event_id=stripe_event_id, metadata={"tier": tier, "package": pkg_id})
    return {"user": email or wallet, "tier": tier}


async def handle_subscription_created(event_data: dict, stripe_event_id: str):
    """customer.subscription.created → active or trialing"""
    customer_id = event_data.get("customer")
    status = event_data.get("status", "active")
    subscription_id = event_data.get("id")
    period_end = event_data.get("current_period_end")

    user = await find_user_by_stripe_customer(customer_id)
    email = user.get("email") if user else None
    wallet = user.get("wallet_address") if user else None

    sub_status = STATUS_TRIALING if status == "trialing" else STATUS_ACTIVE
    end_dt = datetime.fromtimestamp(period_end, tz=timezone.utc) if period_end else None

    await update_subscription_status(
        user_id=wallet, email=email, status=sub_status,
        period_end=end_dt, stripe_subscription_id=subscription_id,
        reason="subscription_created",
    )
    await broadcast_admin_event("subscription_activated", user_id=email or wallet, stripe_event_id=stripe_event_id, metadata={"status": sub_status})
    return {"user": email or wallet, "status": sub_status}


async def handle_subscription_updated(event_data: dict, stripe_event_id: str):
    """customer.subscription.updated → sync status"""
    customer_id = event_data.get("customer")
    status = event_data.get("status", "active")
    subscription_id = event_data.get("id")
    period_end = event_data.get("current_period_end")
    cancel_at_period_end = event_data.get("cancel_at_period_end", False)

    user = await find_user_by_stripe_customer(customer_id)
    email = user.get("email") if user else None
    wallet = user.get("wallet_address") if user else None

    status_map = {
        "active": STATUS_ACTIVE,
        "trialing": STATUS_TRIALING,
        "past_due": STATUS_PAST_DUE,
        "canceled": STATUS_CANCELED,
        "unpaid": STATUS_PAST_DUE,
    }
    sub_status = status_map.get(status, STATUS_ACTIVE)
    end_dt = datetime.fromtimestamp(period_end, tz=timezone.utc) if period_end else None

    # Determine tier from current user
    tier = user.get("user_tier", "pro") if user else "pro"
    if sub_status == STATUS_CANCELED:
        tier = "free"

    await update_subscription_status(
        user_id=wallet, email=email, status=sub_status,
        tier=tier if sub_status in (STATUS_ACTIVE, STATUS_CANCELED) else None,
        period_end=end_dt, stripe_subscription_id=subscription_id,
        reason="subscription_updated",
    )
    await broadcast_admin_event("subscription_updated", user_id=email or wallet, stripe_event_id=stripe_event_id, metadata={"status": sub_status, "cancel_at_period_end": cancel_at_period_end})

    if sub_status == STATUS_PAST_DUE:
        await broadcast_admin_event("subscription_past_due", user_id=email or wallet, stripe_event_id=stripe_event_id)

    return {"user": email or wallet, "status": sub_status}


async def handle_subscription_deleted(event_data: dict, stripe_event_id: str):
    """customer.subscription.deleted → canceled"""
    customer_id = event_data.get("customer")
    subscription_id = event_data.get("id")

    user = await find_user_by_stripe_customer(customer_id)
    email = user.get("email") if user else None
    wallet = user.get("wallet_address") if user else None

    await update_subscription_status(
        user_id=wallet, email=email, status=STATUS_CANCELED, tier="free",
        stripe_subscription_id=subscription_id, reason="subscription_deleted",
    )
    await broadcast_admin_event("subscription_canceled", user_id=email or wallet, stripe_event_id=stripe_event_id)
    return {"user": email or wallet, "status": STATUS_CANCELED}


async def handle_invoice_payment_succeeded(event_data: dict, stripe_event_id: str):
    """invoice.payment_succeeded → extend subscription"""
    customer_id = event_data.get("customer")
    subscription_id = event_data.get("subscription")
    amount_paid = event_data.get("amount_paid", 0)
    period_end = event_data.get("lines", {}).get("data", [{}])[0].get("period", {}).get("end") if event_data.get("lines") else None

    user = await find_user_by_stripe_customer(customer_id)
    email = user.get("email") if user else None
    wallet = user.get("wallet_address") if user else None

    end_dt = datetime.fromtimestamp(period_end, tz=timezone.utc) if period_end else None

    await update_subscription_status(
        user_id=wallet, email=email, status=STATUS_ACTIVE,
        period_end=end_dt, stripe_subscription_id=subscription_id,
        reason="payment_succeeded",
    )
    await broadcast_admin_event("subscription_activated", user_id=email or wallet, stripe_event_id=stripe_event_id, metadata={"amount": amount_paid / 100, "period_end": end_dt.isoformat() if end_dt else None})
    return {"user": email or wallet, "amount": amount_paid / 100}


async def handle_invoice_payment_failed(event_data: dict, stripe_event_id: str):
    """invoice.payment_failed → past_due"""
    customer_id = event_data.get("customer")
    subscription_id = event_data.get("subscription")
    attempt_count = event_data.get("attempt_count", 0)

    user = await find_user_by_stripe_customer(customer_id)
    email = user.get("email") if user else None
    wallet = user.get("wallet_address") if user else None

    await update_subscription_status(
        user_id=wallet, email=email, status=STATUS_PAST_DUE,
        stripe_subscription_id=subscription_id, reason="payment_failed",
    )
    await broadcast_admin_event("payment_failed", user_id=email or wallet, stripe_event_id=stripe_event_id, metadata={"attempt_count": attempt_count})

    # Founder alert for payment failure
    asyncio.create_task(send_founder_stripe_alert(
        "invoice.payment_failed", stripe_event_id,
        user_id=email or wallet,
        error_details=f"Payment failed after {attempt_count} attempts",
    ))
    return {"user": email or wallet, "status": STATUS_PAST_DUE}


async def handle_trial_will_end(event_data: dict, stripe_event_id: str):
    """customer.subscription.trial_will_end → info broadcast"""
    customer_id = event_data.get("customer")
    trial_end = event_data.get("trial_end")

    user = await find_user_by_stripe_customer(customer_id)
    email = user.get("email") if user else None

    end_dt = datetime.fromtimestamp(trial_end, tz=timezone.utc) if trial_end else None
    await broadcast_admin_event("subscription_updated", user_id=email, stripe_event_id=stripe_event_id, metadata={"trial_ends": end_dt.isoformat() if end_dt else None, "type": "trial_will_end"})
    return {"user": email, "trial_end": end_dt.isoformat() if end_dt else None}


async def handle_charge_refunded(event_data: dict, stripe_event_id: str):
    """charge.refunded → cancel if full refund"""
    customer_id = event_data.get("customer")
    amount_refunded = event_data.get("amount_refunded", 0)
    amount = event_data.get("amount", 0)
    is_full_refund = amount_refunded >= amount and amount > 0

    user = await find_user_by_stripe_customer(customer_id)
    email = user.get("email") if user else None
    wallet = user.get("wallet_address") if user else None

    if is_full_refund:
        await update_subscription_status(
            user_id=wallet, email=email, status=STATUS_CANCELED, tier="free",
            reason="full_refund",
        )

    await broadcast_admin_event("refund_processed", user_id=email or wallet, stripe_event_id=stripe_event_id, metadata={"amount_refunded": amount_refunded / 100, "full_refund": is_full_refund})

    # Founder alert for refund
    asyncio.create_task(send_founder_stripe_alert(
        "charge.refunded", stripe_event_id,
        user_id=email or wallet,
        error_details=f"Refunded ${amount_refunded / 100:.2f} ({'full' if is_full_refund else 'partial'} refund)",
    ))
    return {"user": email or wallet, "full_refund": is_full_refund}


async def handle_charge_dispute_created(event_data: dict, stripe_event_id: str):
    """charge.dispute.created → flag subscription"""
    # Try to find customer via the charge's customer field
    customer_id = event_data.get("customer") or event_data.get("payment_intent")
    amount = event_data.get("amount", 0)
    reason = event_data.get("reason", "unknown")
    user = await find_user_by_stripe_customer(customer_id) if customer_id else None
    email = user.get("email") if user else None
    wallet = user.get("wallet_address") if user else None

    if email or wallet:
        await update_subscription_status(
            user_id=wallet, email=email, status=STATUS_FLAGGED,
            reason="dispute_created",
        )

    await broadcast_admin_event("dispute_created", user_id=email or wallet, stripe_event_id=stripe_event_id, metadata={"amount": amount / 100, "reason": reason})

    # Founder alert for dispute
    asyncio.create_task(send_founder_stripe_alert(
        "charge.dispute.created", stripe_event_id,
        user_id=email or wallet,
        error_details=f"Dispute: {reason}, amount: ${amount / 100:.2f}",
    ))
    return {"user": email or wallet, "status": STATUS_FLAGGED}


# ── Main Dispatch ──────────────────────────────────────────────

EVENT_HANDLERS = {
    "checkout.session.completed": handle_checkout_session_completed,
    "customer.subscription.created": handle_subscription_created,
    "customer.subscription.updated": handle_subscription_updated,
    "customer.subscription.deleted": handle_subscription_deleted,
    "invoice.payment_succeeded": handle_invoice_payment_succeeded,
    "invoice.payment_failed": handle_invoice_payment_failed,
    "customer.subscription.trial_will_end": handle_trial_will_end,
    "charge.refunded": handle_charge_refunded,
    "charge.dispute.created": handle_charge_dispute_created,
}


async def process_webhook_event(payload: bytes, signature: str, is_demo: bool = False) -> dict:
    """
    Main entry point for processing Stripe webhook events.
    Returns {"status": "ok", ...} on success, raises on failure.
    """
    # 1. Parse event
    try:
        if STRIPE_WEBHOOK_SECRET and signature and not is_demo:
            event = verify_stripe_signature(payload, signature)
        else:
            import json
            event = json.loads(payload)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Stripe signature verification failed: {e}")
        asyncio.create_task(send_founder_stripe_alert(
            "signature_verification_failure", "N/A",
            error_details=str(e), is_demo=is_demo,
        ))
        raise ValueError(f"Signature verification failed: {e}")
    except Exception as e:
        logger.error(f"Failed to parse webhook payload: {e}")
        raise ValueError(f"Invalid webhook payload: {e}")

    event_id = event.get("id", "")
    event_type = event.get("type", "unknown")
    event_data = event.get("data", {}).get("object", {})

    # 2. Idempotency check
    if await is_event_processed(event_id):
        logger.info(f"Duplicate event skipped: {event_id}")
        return {"status": "ok", "message": "duplicate", "event_id": event_id}

    # 3. Log to traffic_events
    user_hint = event_data.get("customer_email") or event_data.get("customer") or None
    await log_stripe_event(event_type, event_id, user_id=user_hint, metadata={"is_demo": is_demo})

    # 4. Broadcast receipt to admin
    await broadcast_admin_event("stripe_event_received", stripe_event_id=event_id, metadata={"event_type": event_type})

    # 5. Dispatch to handler
    handler = EVENT_HANDLERS.get(event_type)
    if handler:
        try:
            result = await handler(event_data, event_id)
            await mark_event_processed(event_id, event_type, metadata=result)
            logger.info(f"Processed webhook: {event_type} ({event_id})")
            return {"status": "ok", "event_type": event_type, "event_id": event_id, **(result or {})}
        except Exception as e:
            logger.error(f"Error processing {event_type}: {e}")
            asyncio.create_task(send_founder_stripe_alert(
                event_type, event_id,
                error_details=f"Handler error: {str(e)}",
                is_demo=is_demo,
            ))
            # Still mark as processed to avoid infinite retries
            await mark_event_processed(event_id, event_type, metadata={"error": str(e)})
            raise
    else:
        # Unhandled event type
        logger.warning(f"Unhandled Stripe event type: {event_type}")
        asyncio.create_task(send_founder_stripe_alert(
            event_type, event_id,
            error_details=f"Unhandled event type: {event_type}",
            is_demo=is_demo,
        ))
        await mark_event_processed(event_id, event_type, metadata={"unhandled": True})
        return {"status": "ok", "message": "unhandled_event", "event_type": event_type}
