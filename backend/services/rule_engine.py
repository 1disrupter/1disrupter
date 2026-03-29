"""
AlphaAI Rule Engine — Real-time anomaly detection.
Runs every 5 seconds, evaluates rules against recent traffic_events,
emits ALERT events and triggers founder email notifications.
"""
import os
import asyncio
import logging
import time
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("AlphaAI.RuleEngine")

# Database reference — set from server.py
db = None

def init_db(database):
    global db
    db = database

# ── Configuration ───────────────────────────────────────────────

RULES_ENABLED = True
CHECK_INTERVAL = 5  # seconds

# Thresholds (tunable)
ERROR_SPIKE_COUNT = 10
ERROR_SPIKE_WINDOW = 60  # seconds
TRAFFIC_SURGE_THRESHOLD = 100  # page_views in 60s
API_SURGE_THRESHOLD = 200  # api_calls in 60s
DISCONNECT_STORM_COUNT = 15
DISCONNECT_STORM_WINDOW = 30
STRATEGY_FLOOD_COUNT = 20
STRATEGY_FLOOD_WINDOW = 30
CHECKOUT_FAILURE_COUNT = 5
CHECKOUT_FAILURE_WINDOW = 600  # 10 minutes
SUSPICIOUS_API_CALLS = 50  # from same user in 10s
SUSPICIOUS_FOLLOW_EVENTS = 10  # from same user in 60s

# Cooldown: minimum seconds between same alert type
COOLDOWN_SECONDS = 120

# ── State ───────────────────────────────────────────────────────

_last_alert_time = {}  # alert_type -> timestamp (epoch)
_active_alerts = set()  # set of currently active alert_types


def _in_cooldown(alert_type: str) -> bool:
    last = _last_alert_time.get(alert_type, 0)
    return (time.time() - last) < COOLDOWN_SECONDS


def _mark_fired(alert_type: str):
    _last_alert_time[alert_type] = time.time()
    _active_alerts.add(alert_type)


def _clear_alert(alert_type: str):
    _active_alerts.discard(alert_type)


def get_active_alerts() -> list:
    return list(_active_alerts)


# ── Alert Emitter ───────────────────────────────────────────────

async def _emit_alert(alert_type: str, message: str, metadata: dict):
    """Insert ALERT event into traffic_events and broadcast to admin WS."""
    from services.admin_events_manager import admin_events_manager

    now = datetime.now(timezone.utc)
    doc = {
        "id": f"alert-{alert_type}-{int(now.timestamp())}",
        "type": "alert",
        "user_id": None,
        "timestamp": now,
        "metadata": {
            "alert_type": alert_type,
            "message": message,
            **metadata,
        },
    }

    # Insert to DB
    try:
        await db.traffic_events.insert_one(doc)
    except Exception as e:
        logger.error(f"Failed to insert alert: {e}")

    # Broadcast to admin WS
    ws_payload = {
        "id": doc["id"],
        "type": "alert",
        "user_id": None,
        "timestamp": now.isoformat(),
        "metadata": doc["metadata"],
    }
    try:
        await admin_events_manager.broadcast_event(ws_payload)
    except Exception as e:
        logger.error(f"Failed to broadcast alert: {e}")

    # Trigger founder email (non-demo only)
    is_demo = metadata.get("demo", False)
    if not is_demo:
        asyncio.create_task(_send_founder_email(alert_type, message, metadata, now))
    else:
        logger.info(f"Demo mode: founder alert suppressed for {alert_type}")

    _mark_fired(alert_type)
    logger.warning(f"ALERT [{alert_type}]: {message}")


async def _send_founder_email(alert_type: str, message: str, metadata: dict, timestamp: datetime):
    """Send alert email to founder via Resend. Retries 3 times."""
    founder_email = os.environ.get("FOUNDER_ALERT_EMAIL", "")
    if not founder_email:
        logger.info("FOUNDER_ALERT_EMAIL not set, skipping email")
        return

    try:
        from services.email_service import send_email
    except ImportError:
        logger.error("email_service not available")
        return

    subject = f"[AlphaAI ALERT] {alert_type.replace('_', ' ').title()}"
    count = metadata.get("count", "N/A")
    window = metadata.get("window", "N/A")
    samples = metadata.get("sample_events", [])
    sample_html = "".join(f"<li>{s}</li>" for s in samples[:5])

    html = f"""
    <div style="font-family: -apple-system, sans-serif; max-width: 600px; margin: 0 auto; background: #0a0a0a; color: #e4e4e7; padding: 32px; border-radius: 12px;">
      <div style="border-left: 4px solid #ef4444; padding-left: 16px; margin-bottom: 24px;">
        <h2 style="color: #ef4444; margin: 0 0 4px 0; font-size: 18px;">Alert: {alert_type.replace('_', ' ').title()}</h2>
        <p style="color: #a1a1aa; margin: 0; font-size: 13px;">{timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
      </div>
      <p style="color: #e4e4e7; font-size: 14px; line-height: 1.6;">{message}</p>
      <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
        <tr><td style="padding: 8px; color: #a1a1aa; font-size: 12px;">Count</td><td style="padding: 8px; font-weight: bold; font-size: 14px;">{count}</td></tr>
        <tr><td style="padding: 8px; color: #a1a1aa; font-size: 12px;">Window</td><td style="padding: 8px; font-weight: bold; font-size: 14px;">{window}</td></tr>
      </table>
      {"<div style='margin-top: 16px;'><p style='color: #a1a1aa; font-size: 12px; margin-bottom: 8px;'>Sample events:</p><ul style='color: #e4e4e7; font-size: 12px; padding-left: 20px;'>" + sample_html + "</ul></div>" if samples else ""}
      <hr style="border: none; border-top: 1px solid #27272a; margin: 24px 0;" />
      <p style="color: #52525b; font-size: 11px;">AlphaAI Monitoring System — <a href='{os.environ.get("APP_URL", "")}/admin/traffic' style='color: #7B61FF;'>View Dashboard</a></p>
    </div>
    """

    for attempt in range(3):
        try:
            result = await send_email(founder_email, subject, html)
            if result.get("status") in ("sent", "logged"):
                logger.info(f"Founder alert email sent for {alert_type}")
                return
        except Exception as e:
            logger.error(f"Founder email attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                await asyncio.sleep(2)

    logger.error(f"Failed to send founder email for {alert_type} after 3 attempts")


# ── Rule Evaluators ─────────────────────────────────────────────

async def _check_error_spike():
    if _in_cooldown("error_spike"):
        return
    since = datetime.now(timezone.utc) - timedelta(seconds=ERROR_SPIKE_WINDOW)
    count = await db.traffic_events.count_documents({
        "type": "error",
        "timestamp": {"$gte": since},
    })
    if count >= ERROR_SPIKE_COUNT:
        samples = await db.traffic_events.find(
            {"type": "error", "timestamp": {"$gte": since}},
            {"_id": 0, "metadata.message": 1, "metadata.source": 1},
        ).limit(5).to_list(5)
        sample_list = [f"{s.get('metadata', {}).get('source', '?')}: {s.get('metadata', {}).get('message', '?')}" for s in samples]
        await _emit_alert("error_spike", f"{count} errors in last {ERROR_SPIKE_WINDOW}s — possible system failure", {
            "count": count, "window": f"{ERROR_SPIKE_WINDOW}s", "sample_events": sample_list,
        })
    else:
        _clear_alert("error_spike")


async def _check_traffic_surge():
    if _in_cooldown("traffic_surge"):
        return
    since = datetime.now(timezone.utc) - timedelta(seconds=60)
    pipeline = [
        {"$match": {"type": {"$in": ["page_view", "api_call"]}, "timestamp": {"$gte": since}}},
        {"$group": {"_id": "$type", "count": {"$sum": 1}}},
    ]
    results = {doc["_id"]: doc["count"] async for doc in db.traffic_events.aggregate(pipeline)}
    pv = results.get("page_view", 0)
    ac = results.get("api_call", 0)

    if pv >= TRAFFIC_SURGE_THRESHOLD or ac >= API_SURGE_THRESHOLD:
        await _emit_alert("traffic_surge", f"Traffic surge detected — {pv} page views, {ac} API calls in last 60s", {
            "count": pv + ac, "window": "60s", "page_views": pv, "api_calls": ac,
        })
    else:
        _clear_alert("traffic_surge")


async def _check_disconnect_storm():
    if _in_cooldown("disconnect_storm"):
        return
    since = datetime.now(timezone.utc) - timedelta(seconds=DISCONNECT_STORM_WINDOW)
    count = await db.traffic_events.count_documents({
        "type": "ws_disconnect",
        "timestamp": {"$gte": since},
    })
    if count >= DISCONNECT_STORM_COUNT:
        await _emit_alert("disconnect_storm", f"{count} WebSocket disconnects in last {DISCONNECT_STORM_WINDOW}s", {
            "count": count, "window": f"{DISCONNECT_STORM_WINDOW}s",
        })
    else:
        _clear_alert("disconnect_storm")


async def _check_strategy_flood():
    if _in_cooldown("strategy_flood"):
        return
    since = datetime.now(timezone.utc) - timedelta(seconds=STRATEGY_FLOOD_WINDOW)
    pipeline = [
        {"$match": {"type": "signal", "timestamp": {"$gte": since}}},
        {"$group": {"_id": "$metadata.strategy_id", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": STRATEGY_FLOOD_COUNT}}},
    ]
    floods = [doc async for doc in db.traffic_events.aggregate(pipeline)]
    if floods:
        top = floods[0]
        await _emit_alert("strategy_flood", f"Strategy {top['_id'][:8] if top['_id'] else '?'}... sent {top['count']} signals in {STRATEGY_FLOOD_WINDOW}s", {
            "count": top["count"], "window": f"{STRATEGY_FLOOD_WINDOW}s", "strategy_id": top["_id"],
        })
    else:
        _clear_alert("strategy_flood")


async def _check_checkout_failures():
    if _in_cooldown("checkout_failures"):
        return
    since = datetime.now(timezone.utc) - timedelta(seconds=CHECKOUT_FAILURE_WINDOW)
    starts = await db.traffic_events.count_documents({"type": "checkout_start", "timestamp": {"$gte": since}})
    successes = await db.traffic_events.count_documents({"type": "checkout_success", "timestamp": {"$gte": since}})
    failures = starts - successes
    if failures >= CHECKOUT_FAILURE_COUNT and starts > 0:
        rate = round((failures / starts) * 100, 1)
        await _emit_alert("checkout_failures", f"{failures} failed checkouts out of {starts} attempts ({rate}% failure rate) in last {CHECKOUT_FAILURE_WINDOW // 60} min", {
            "count": failures, "window": f"{CHECKOUT_FAILURE_WINDOW // 60}min", "starts": starts, "successes": successes, "failure_rate": rate,
        })
    else:
        _clear_alert("checkout_failures")


async def _check_suspicious_behavior():
    if _in_cooldown("suspicious_behavior"):
        return
    since_10s = datetime.now(timezone.utc) - timedelta(seconds=10)
    since_60s = datetime.now(timezone.utc) - timedelta(seconds=60)

    # Check excessive API calls from single user
    api_pipeline = [
        {"$match": {"type": "api_call", "timestamp": {"$gte": since_10s}, "user_id": {"$ne": None}}},
        {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": SUSPICIOUS_API_CALLS}}},
    ]
    api_abusers = [doc async for doc in db.traffic_events.aggregate(api_pipeline)]

    # Check excessive follow/unfollow from single user
    follow_pipeline = [
        {"$match": {"type": {"$in": ["follow", "unfollow"]}, "timestamp": {"$gte": since_60s}, "user_id": {"$ne": None}}},
        {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": SUSPICIOUS_FOLLOW_EVENTS}}},
    ]
    follow_abusers = [doc async for doc in db.traffic_events.aggregate(follow_pipeline)]

    if api_abusers or follow_abusers:
        samples = []
        if api_abusers:
            samples.append(f"User {api_abusers[0]['_id'][:8]}...: {api_abusers[0]['count']} API calls in 10s")
        if follow_abusers:
            samples.append(f"User {follow_abusers[0]['_id'][:8]}...: {follow_abusers[0]['count']} follow/unfollow in 60s")
        await _emit_alert("suspicious_behavior", "Suspicious user behavior detected — possible abuse", {
            "count": len(api_abusers) + len(follow_abusers), "window": "10-60s", "sample_events": samples,
        })
    else:
        _clear_alert("suspicious_behavior")


# ── Main Loop ───────────────────────────────────────────────────

ALL_RULES = [
    _check_error_spike,
    _check_traffic_surge,
    _check_disconnect_storm,
    _check_strategy_flood,
    _check_checkout_failures,
    _check_suspicious_behavior,
]


async def rule_engine_loop():
    """Background task: runs every 5 seconds, evaluates all rules."""
    logger.info("Rule engine started")
    while True:
        try:
            if db is not None:
                await asyncio.gather(*[rule() for rule in ALL_RULES], return_exceptions=True)
        except Exception as e:
            logger.error(f"Rule engine error: {e}")
        await asyncio.sleep(CHECK_INTERVAL)
