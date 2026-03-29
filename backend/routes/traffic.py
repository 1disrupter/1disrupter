"""
AlphaAI Admin Traffic Analytics
Event logging, aggregated summaries, and timeseries data for the Admin Traffic Dashboard.
"""
import os
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

logger = logging.getLogger("AlphaAI.Traffic")

router = APIRouter(prefix="/api/admin", tags=["traffic"])

ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "alphaai_admin_2026")

# Database reference (set in server.py startup)
db = None

def init_db(database):
    global db
    db = database


# ── Models ─────────────────────────────────────────────────────

class TrafficEvent(BaseModel):
    type: str = Field(..., description="page_view, api_call, strategy_view, follow, unfollow, signal, ws_connect, ws_disconnect, upgrade_prompt, checkout_start, checkout_success, error")
    metadata: dict = Field(default_factory=dict)


# ── Helpers ────────────────────────────────────────────────────

def _range_to_dt(range_val: str) -> datetime:
    now = datetime.now(timezone.utc)
    if range_val == "24h":
        return now - timedelta(hours=24)
    if range_val == "7d":
        return now - timedelta(days=7)
    return now - timedelta(days=30)


def _bucket_format(range_val: str) -> tuple:
    """Return (mongo date format, python strftime) for time bucketing."""
    if range_val == "24h":
        return "%Y-%m-%dT%H:00", "%H:00"
    if range_val == "7d":
        return "%Y-%m-%d", "%m/%d"
    return "%Y-%m-%d", "%m/%d"


async def _verify_admin(admin_key: str):
    if admin_key != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Admin access denied")


# ── POST /events — log any event ───────────────────────────────

@router.post("/events")
async def log_event(event: TrafficEvent, request: Request):
    """Log a traffic event. Auth optional — demo events tagged automatically."""
    user_id = None

    # Try to extract user from Bearer token
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            from routes.auth import decode_token, get_user_by_id
            payload = decode_token(auth_header.split(" ")[1])
            if payload and payload.get("type") == "access":
                user = await get_user_by_id(payload.get("sub"))
                if user:
                    user_id = user["id"]
        except Exception:
            pass  # Anonymous event

    doc = {
        "id": str(uuid.uuid4()),
        "type": event.type,
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc),
        "metadata": event.metadata,
    }
    await db.traffic_events.insert_one(doc)
    return {"success": True, "event_id": doc["id"]}


# ── GET /traffic/summary — aggregated metrics ──────────────────

@router.get("/traffic/summary")
async def traffic_summary(
    admin_key: str = Query(...),
    range: str = Query("24h", alias="range"),
):
    await _verify_admin(admin_key)
    since = _range_to_dt(range)

    pipeline = [
        {"$match": {"timestamp": {"$gte": since}}},
        {"$group": {
            "_id": "$type",
            "count": {"$sum": 1},
            "unique_users": {"$addToSet": "$user_id"},
        }},
    ]
    cursor = db.traffic_events.aggregate(pipeline)
    buckets = {doc["_id"]: doc async for doc in cursor}

    def _count(t):
        return buckets.get(t, {}).get("count", 0)

    def _users(t):
        s = buckets.get(t, {}).get("unique_users", [])
        return len([u for u in s if u is not None])

    # Total unique users across all events
    all_users = set()
    for b in buckets.values():
        all_users.update(u for u in b.get("unique_users", []) if u is not None)

    # Demo sessions = events where metadata.demo == true
    demo_pipeline = [
        {"$match": {"timestamp": {"$gte": since}, "metadata.demo": True}},
        {"$group": {"_id": None, "count": {"$sum": 1}, "users": {"$addToSet": "$user_id"}}},
    ]
    demo_result = await db.traffic_events.aggregate(demo_pipeline).to_list(1)
    demo_sessions = demo_result[0]["count"] if demo_result else 0

    # Error events with latency data
    latency_pipeline = [
        {"$match": {"timestamp": {"$gte": since}, "type": "api_call", "metadata.latency_ms": {"$exists": True}}},
        {"$group": {
            "_id": None,
            "avg_latency": {"$avg": "$metadata.latency_ms"},
            "max_latency": {"$max": "$metadata.latency_ms"},
            "count": {"$sum": 1},
        }},
    ]
    latency_result = await db.traffic_events.aggregate(latency_pipeline).to_list(1)
    avg_latency = round(latency_result[0]["avg_latency"], 1) if latency_result else 0
    p95_latency = round(latency_result[0].get("max_latency", 0), 1) if latency_result else 0

    return {
        "range": range,
        "total_events": sum(b.get("count", 0) for b in buckets.values()),
        "unique_users": len(all_users),
        "page_views": _count("page_view"),
        "api_calls": _count("api_call"),
        "ws_connections": _count("ws_connect"),
        "ws_disconnections": _count("ws_disconnect"),
        "strategy_views": _count("strategy_view"),
        "follows": _count("follow"),
        "unfollows": _count("unfollow"),
        "signals_delivered": _count("signal"),
        "upgrade_prompts": _count("upgrade_prompt"),
        "checkout_starts": _count("checkout_start"),
        "checkout_successes": _count("checkout_success"),
        "errors": _count("error"),
        "demo_sessions": demo_sessions,
        "avg_latency_ms": avg_latency,
        "p95_latency_ms": p95_latency,
    }


# ── GET /traffic/timeseries — time-bucketed data ───────────────

@router.get("/traffic/timeseries")
async def traffic_timeseries(
    admin_key: str = Query(...),
    range: str = Query("24h", alias="range"),
):
    await _verify_admin(admin_key)
    since = _range_to_dt(range)
    fmt_mongo, _ = _bucket_format(range)

    pipeline = [
        {"$match": {"timestamp": {"$gte": since}}},
        {"$group": {
            "_id": {
                "bucket": {"$dateToString": {"format": fmt_mongo, "date": "$timestamp"}},
                "type": "$type",
            },
            "count": {"$sum": 1},
        }},
        {"$sort": {"_id.bucket": 1}},
    ]

    cursor = db.traffic_events.aggregate(pipeline)
    raw = [doc async for doc in cursor]

    # Reshape into {bucket: {type: count, ...}}
    buckets_map = {}
    for doc in raw:
        bucket = doc["_id"]["bucket"]
        event_type = doc["_id"]["type"]
        if bucket not in buckets_map:
            buckets_map[bucket] = {"time": bucket}
        buckets_map[bucket][event_type] = doc["count"]

    series = sorted(buckets_map.values(), key=lambda x: x["time"])

    return {"range": range, "series": series}


# ── GET /traffic/events — raw paginated events ─────────────────

@router.get("/traffic/events")
async def traffic_events(
    admin_key: str = Query(...),
    event_type: Optional[str] = Query(None, alias="type"),
    user_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100),
):
    await _verify_admin(admin_key)
    query = {}
    if event_type:
        query["type"] = event_type
    if user_id:
        query["user_id"] = user_id

    total = await db.traffic_events.count_documents(query)
    skip = (page - 1) * limit
    items = await db.traffic_events.find(query, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)

    # Convert datetime to string for JSON serialization
    for item in items:
        if isinstance(item.get("timestamp"), datetime):
            item["timestamp"] = item["timestamp"].isoformat()

    return {
        "events": items,
        "total": total,
        "page": page,
        "pages": max(1, (total + limit - 1) // limit),
    }
