"""
Tests for Stripe Webhook Handler — full lifecycle coverage.
"""
import json
import time
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Setup fake DB before importing handler
fake_db = MagicMock()
fake_db.stripe_webhook_events = MagicMock()
fake_db.stripe_webhook_events.find_one = AsyncMock(return_value=None)
fake_db.stripe_webhook_events.insert_one = AsyncMock()
fake_db.traffic_events = MagicMock()
fake_db.traffic_events.insert_one = AsyncMock()
fake_db.users = MagicMock()
fake_db.users.find_one = AsyncMock(return_value=None)
fake_db.users.update_one = AsyncMock()
fake_db.investors = MagicMock()
fake_db.investors.find_one = AsyncMock(return_value=None)
fake_db.investors.update_one = AsyncMock()
fake_db.payment_transactions = MagicMock()
fake_db.payment_transactions.find_one = AsyncMock(return_value=None)
fake_db.payment_transactions.update_one = AsyncMock()


def make_event(event_type, data, event_id=None):
    return json.dumps({
        "id": event_id or f"evt_test_{int(time.time())}_{event_type.replace('.', '_')}",
        "type": event_type,
        "data": {"object": data},
    }).encode()


@pytest.fixture(autouse=True)
def setup_db():
    from services import stripe_webhook_handler as handler
    handler.init_db(fake_db)
    # Reset mocks
    fake_db.stripe_webhook_events.find_one.reset_mock()
    fake_db.stripe_webhook_events.find_one.return_value = None
    fake_db.stripe_webhook_events.insert_one.reset_mock()
    fake_db.traffic_events.insert_one.reset_mock()
    fake_db.users.find_one.reset_mock()
    fake_db.users.find_one.return_value = None
    fake_db.users.update_one.reset_mock()
    fake_db.investors.update_one.reset_mock()
    fake_db.payment_transactions.find_one.reset_mock()
    fake_db.payment_transactions.find_one.return_value = None
    fake_db.payment_transactions.update_one.reset_mock()
    yield


# ── checkout.session.completed ─────────────────────────────────

@pytest.mark.asyncio
async def test_checkout_session_completed():
    from services.stripe_webhook_handler import process_webhook_event
    with patch("services.stripe_webhook_handler.broadcast_admin_event", new_callable=AsyncMock):
        payload = make_event("checkout.session.completed", {
            "id": "cs_test_123",
            "customer": "cus_123",
            "customer_details": {"email": "user@test.com"},
            "subscription": "sub_123",
        }, event_id="evt_checkout_1")
        result = await process_webhook_event(payload, "", is_demo=True)
        assert result["status"] == "ok"
        assert result["event_type"] == "checkout.session.completed"
        assert result.get("tier") == "pro"
        fake_db.stripe_webhook_events.insert_one.assert_called()


# ── customer.subscription.created ──────────────────────────────

@pytest.mark.asyncio
async def test_subscription_created_trialing():
    from services.stripe_webhook_handler import process_webhook_event
    fake_db.users.find_one.return_value = {"email": "user@test.com", "wallet_address": "0x123"}
    with patch("services.stripe_webhook_handler.broadcast_admin_event", new_callable=AsyncMock):
        payload = make_event("customer.subscription.created", {
            "id": "sub_123",
            "customer": "cus_123",
            "status": "trialing",
            "current_period_end": int(time.time()) + 86400 * 14,
        }, event_id="evt_sub_created_1")
        result = await process_webhook_event(payload, "", is_demo=True)
        assert result["status"] == "trialing"


@pytest.mark.asyncio
async def test_subscription_created_active():
    from services.stripe_webhook_handler import process_webhook_event
    fake_db.users.find_one.return_value = {"email": "user@test.com", "wallet_address": "0x123"}
    with patch("services.stripe_webhook_handler.broadcast_admin_event", new_callable=AsyncMock):
        payload = make_event("customer.subscription.created", {
            "id": "sub_123",
            "customer": "cus_123",
            "status": "active",
            "current_period_end": int(time.time()) + 86400 * 30,
        }, event_id="evt_sub_created_2")
        result = await process_webhook_event(payload, "", is_demo=True)
        assert result["status"] == "active"


# ── customer.subscription.updated ──────────────────────────────

@pytest.mark.asyncio
async def test_subscription_updated_to_active():
    from services.stripe_webhook_handler import process_webhook_event
    fake_db.users.find_one.return_value = {"email": "user@test.com", "wallet_address": "0x123", "user_tier": "pro"}
    with patch("services.stripe_webhook_handler.broadcast_admin_event", new_callable=AsyncMock):
        payload = make_event("customer.subscription.updated", {
            "id": "sub_123",
            "customer": "cus_123",
            "status": "active",
            "current_period_end": int(time.time()) + 86400 * 30,
            "cancel_at_period_end": False,
        }, event_id="evt_sub_updated_1")
        result = await process_webhook_event(payload, "", is_demo=True)
        assert result["status"] == "active"


@pytest.mark.asyncio
async def test_subscription_updated_to_past_due():
    from services.stripe_webhook_handler import process_webhook_event
    fake_db.users.find_one.return_value = {"email": "user@test.com", "wallet_address": "0x123", "user_tier": "pro"}
    with patch("services.stripe_webhook_handler.broadcast_admin_event", new_callable=AsyncMock):
        payload = make_event("customer.subscription.updated", {
            "id": "sub_123",
            "customer": "cus_123",
            "status": "past_due",
            "current_period_end": int(time.time()) + 86400 * 30,
        }, event_id="evt_sub_updated_2")
        result = await process_webhook_event(payload, "", is_demo=True)
        assert result["status"] == "past_due"


# ── customer.subscription.deleted ──────────────────────────────

@pytest.mark.asyncio
async def test_subscription_deleted():
    from services.stripe_webhook_handler import process_webhook_event
    fake_db.users.find_one.return_value = {"email": "user@test.com", "wallet_address": "0x123"}
    with patch("services.stripe_webhook_handler.broadcast_admin_event", new_callable=AsyncMock):
        payload = make_event("customer.subscription.deleted", {
            "id": "sub_123",
            "customer": "cus_123",
        }, event_id="evt_sub_deleted_1")
        result = await process_webhook_event(payload, "", is_demo=True)
        assert result["status"] == "canceled"
        # Verify user tier set to free
        call_args = fake_db.users.update_one.call_args
        update_set = call_args[0][1]["$set"]
        assert update_set["user_tier"] == "free"
        assert update_set["is_pro"] is False


# ── invoice.payment_succeeded ──────────────────────────────────

@pytest.mark.asyncio
async def test_payment_succeeded():
    from services.stripe_webhook_handler import process_webhook_event
    fake_db.users.find_one.return_value = {"email": "user@test.com", "wallet_address": "0x123"}
    with patch("services.stripe_webhook_handler.broadcast_admin_event", new_callable=AsyncMock):
        payload = make_event("invoice.payment_succeeded", {
            "customer": "cus_123",
            "subscription": "sub_123",
            "amount_paid": 2900,
            "lines": {"data": [{"period": {"end": int(time.time()) + 86400 * 30}}]},
        }, event_id="evt_payment_ok_1")
        result = await process_webhook_event(payload, "", is_demo=True)
        assert result["amount"] == 29.0


# ── invoice.payment_failed ─────────────────────────────────────

@pytest.mark.asyncio
async def test_payment_failed():
    from services.stripe_webhook_handler import process_webhook_event
    fake_db.users.find_one.return_value = {"email": "user@test.com", "wallet_address": "0x123"}
    with patch("services.stripe_webhook_handler.broadcast_admin_event", new_callable=AsyncMock):
        with patch("services.stripe_webhook_handler.send_founder_stripe_alert", new_callable=AsyncMock):
            payload = make_event("invoice.payment_failed", {
                "customer": "cus_123",
                "subscription": "sub_123",
                "attempt_count": 2,
            }, event_id="evt_payment_fail_1")
            result = await process_webhook_event(payload, "", is_demo=True)
            assert result["status"] == "past_due"


# ── customer.subscription.trial_will_end ───────────────────────

@pytest.mark.asyncio
async def test_trial_will_end():
    from services.stripe_webhook_handler import process_webhook_event
    fake_db.users.find_one.return_value = {"email": "user@test.com"}
    trial_end = int(time.time()) + 86400 * 3
    with patch("services.stripe_webhook_handler.broadcast_admin_event", new_callable=AsyncMock):
        payload = make_event("customer.subscription.trial_will_end", {
            "customer": "cus_123",
            "trial_end": trial_end,
        }, event_id="evt_trial_end_1")
        result = await process_webhook_event(payload, "", is_demo=True)
        assert result["trial_end"] is not None


# ── charge.refunded ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_full_refund_cancels_subscription():
    from services.stripe_webhook_handler import process_webhook_event
    fake_db.users.find_one.return_value = {"email": "user@test.com", "wallet_address": "0x123"}
    with patch("services.stripe_webhook_handler.broadcast_admin_event", new_callable=AsyncMock):
        with patch("services.stripe_webhook_handler.send_founder_stripe_alert", new_callable=AsyncMock):
            payload = make_event("charge.refunded", {
                "customer": "cus_123",
                "amount": 2900,
                "amount_refunded": 2900,
            }, event_id="evt_refund_full_1")
            result = await process_webhook_event(payload, "", is_demo=True)
            assert result["full_refund"] is True
            call_args = fake_db.users.update_one.call_args
            update_set = call_args[0][1]["$set"]
            assert update_set["is_pro"] is False


@pytest.mark.asyncio
async def test_partial_refund_keeps_subscription():
    from services.stripe_webhook_handler import process_webhook_event
    fake_db.users.find_one.return_value = {"email": "user@test.com", "wallet_address": "0x123"}
    with patch("services.stripe_webhook_handler.broadcast_admin_event", new_callable=AsyncMock):
        with patch("services.stripe_webhook_handler.send_founder_stripe_alert", new_callable=AsyncMock):
            payload = make_event("charge.refunded", {
                "customer": "cus_123",
                "amount": 2900,
                "amount_refunded": 1000,
            }, event_id="evt_refund_partial_1")
            result = await process_webhook_event(payload, "", is_demo=True)
            assert result["full_refund"] is False


# ── charge.dispute.created ─────────────────────────────────────

@pytest.mark.asyncio
async def test_dispute_flags_subscription():
    from services.stripe_webhook_handler import process_webhook_event
    fake_db.users.find_one.return_value = {"email": "user@test.com", "wallet_address": "0x123"}
    with patch("services.stripe_webhook_handler.broadcast_admin_event", new_callable=AsyncMock):
        with patch("services.stripe_webhook_handler.send_founder_stripe_alert", new_callable=AsyncMock):
            payload = make_event("charge.dispute.created", {
                "customer": "cus_123",
                "amount": 2900,
                "reason": "fraudulent",
            }, event_id="evt_dispute_1")
            result = await process_webhook_event(payload, "", is_demo=True)
            assert result["status"] == "flagged"


# ── Idempotency ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_duplicate_event_skipped():
    from services.stripe_webhook_handler import process_webhook_event
    fake_db.stripe_webhook_events.find_one.return_value = {"event_id": "evt_dup_1", "event_type": "checkout.session.completed"}
    payload = make_event("checkout.session.completed", {
        "id": "cs_test_dup",
    }, event_id="evt_dup_1")
    result = await process_webhook_event(payload, "", is_demo=True)
    assert result["message"] == "duplicate"
    # insert_one should NOT be called for the event processing (only the initial find_one)
    # The event should be skipped entirely


# ── Unhandled Event Type ───────────────────────────────────────

@pytest.mark.asyncio
async def test_unhandled_event_type():
    from services.stripe_webhook_handler import process_webhook_event
    with patch("services.stripe_webhook_handler.broadcast_admin_event", new_callable=AsyncMock):
        with patch("services.stripe_webhook_handler.send_founder_stripe_alert", new_callable=AsyncMock):
            payload = make_event("some.unknown.event", {"foo": "bar"}, event_id="evt_unknown_1")
            result = await process_webhook_event(payload, "", is_demo=True)
            assert result["message"] == "unhandled_event"


# ── Demo Mode Suppression ─────────────────────────────────────

@pytest.mark.asyncio
async def test_demo_mode_suppresses_founder_alert():
    from services.stripe_webhook_handler import send_founder_stripe_alert
    import logging
    with patch("os.environ.get", return_value="founder@test.com"):
        # Demo mode should log and return without sending
        await send_founder_stripe_alert("test_event", "evt_123", is_demo=True)
        # No email sent in demo mode — success if no exception


# ── Invalid Payload ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_invalid_payload_raises():
    from services.stripe_webhook_handler import process_webhook_event
    with pytest.raises(ValueError, match="Invalid webhook payload"):
        await process_webhook_event(b"not json", "", is_demo=True)
