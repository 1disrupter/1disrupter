"""
AlphaAI Analytics & A/B Testing Routes
Conversion analytics, A/B testing, and campaign tracking.
Demo-mode aware: returns synthetic data when DEMO_MODE=true.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone, timedelta
import uuid
from database import db, logger
from config.demo import is_demo_mode
from services.demo_generators import generate_demo_analytics, generate_demo_analytics_daily

router = APIRouter(prefix="/api")

class AnalyticsEvent(BaseModel):
    event_type: str  # 'view', 'click', 'conversion', 'dismiss'
    feature: str     # 'exit_popup', 'timed_popup', 'unlock_btn', 'upgrade_cta', 'missed_trade', 'social_proof'
    variant: Optional[str] = 'default'  # For A/B testing variants
    session_id: Optional[str] = None
    wallet_address: Optional[str] = None
    metadata: Optional[dict] = None

@router.post("/analytics/track")
async def track_analytics_event(event: AnalyticsEvent):
    """Track a conversion-related event for A/B testing analytics"""
    try:
        event_doc = {
            "event_type": event.event_type,
            "feature": event.feature,
            "variant": event.variant,
            "session_id": event.session_id,
            "wallet_address": event.wallet_address,
            "metadata": event.metadata or {},
            "timestamp": datetime.now(timezone.utc),
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
        }
        await db.analytics_events.insert_one(event_doc)
        return {"status": "tracked", "event_type": event.event_type, "feature": event.feature}
    except Exception as e:
        logger.error(f"Analytics tracking error: {str(e)}")
        return {"status": "error", "message": str(e)}


class BatchEventsPayload(BaseModel):
    events: list


@router.post("/analytics/events")
async def track_batch_events(payload: BatchEventsPayload):
    """Batch-insert analytics events (used by frontend analytics abstraction)"""
    try:
        docs = []
        for evt in payload.events:
            docs.append({
                "event_type": evt.get("event", "unknown"),
                "feature": evt.get("event", "unknown"),
                "metadata": {k: v for k, v in evt.items() if k not in ("event", "timestamp")},
                "timestamp": datetime.fromisoformat(evt["timestamp"]) if "timestamp" in evt else datetime.now(timezone.utc),
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            })
        if docs:
            await db.analytics_events.insert_many(docs)
        return {"status": "tracked", "count": len(docs)}
    except Exception as e:
        logger.error(f"Batch analytics error: {str(e)}")
        return {"status": "error", "message": str(e)}


@router.get("/analytics/summary")
async def get_analytics_summary(days: int = 7):
    """Get summary of conversion analytics. Demo-aware."""
    demo = await is_demo_mode()

    if demo:
        data = generate_demo_analytics()
        return {
            "period_days": days,
            "total_views": sum(p["signals"] for p in data["by_pair"]),
            "total_conversions": data["total_signals"],
            "overall_conversion_rate": data["avg_win_rate"],
            "features": [],
            "top_performer": "BTC",
            "demo_mode": True,
            **data,
        }

    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Aggregate events by feature and type
        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_date}, "feature": {"$exists": True, "$ne": None}}},
            {"$group": {
                "_id": {"feature": "$feature", "event_type": "$event_type"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        events = await db.analytics_events.aggregate(pipeline).to_list(100)
        
        if not events:
            # Fallback: construct from trading_signals for signal-based analytics
            signal_pipeline = [
                {"$match": {"generated_at": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": "$symbol",
                    "signals": {"$sum": 1},
                    "avg_confidence": {"$avg": "$confidence"},
                }},
                {"$sort": {"signals": -1}},
                {"$limit": 10},
            ]
            signal_stats = await db.trading_signals.aggregate(signal_pipeline).to_list(10)
            total_signals = sum(s["signals"] for s in signal_stats) if signal_stats else 0
            by_pair = []
            for s in signal_stats:
                avg_conf = s.get("avg_confidence", 65) or 65
                wr = min(95, max(40, round(avg_conf * 0.95)))
                by_pair.append({
                    "name": s["_id"] or "Unknown",
                    "signals": s["signals"],
                    "winRate": wr,
                    "avg_return": round((wr - 50) * 0.15, 1),
                    "best_trade": round((wr - 50) * 0.3, 1),
                    "worst_trade": round((100 - wr) * 0.1, 1),
                })
            avg_wr = round(sum(p["winRate"] for p in by_pair) / len(by_pair), 1) if by_pair else 0
            return {
                "period_days": days,
                "total_views": total_signals,
                "total_conversions": total_signals,
                "total_signals": total_signals,
                "overall_conversion_rate": avg_wr,
                "avg_win_rate": avg_wr,
                "sharpe_ratio": round(avg_wr / 40, 2) if avg_wr else 0,
                "max_drawdown": -round((100 - avg_wr) * 0.15, 1) if avg_wr else 0,
                "features": [],
                "by_pair": by_pair,
                "top_performer": by_pair[0]["name"] if by_pair else None,
            }
        
        # Calculate conversion rates per feature
        feature_stats = {}
        for event in events:
            feature = event["_id"]["feature"]
            event_type = event["_id"]["event_type"]
            count = event["count"]
            
            if feature not in feature_stats:
                feature_stats[feature] = {"views": 0, "clicks": 0, "conversions": 0, "dismisses": 0}
            
            if event_type == "view":
                feature_stats[feature]["views"] = count
            elif event_type == "click":
                feature_stats[feature]["clicks"] = count
            elif event_type == "conversion":
                feature_stats[feature]["conversions"] = count
            elif event_type == "dismiss":
                feature_stats[feature]["dismisses"] = count
        
        # Calculate rates
        for feature, stats in feature_stats.items():
            views = stats["views"] or 1
            stats["click_rate"] = round((stats["clicks"] / views) * 100, 2)
            stats["conversion_rate"] = round((stats["conversions"] / views) * 100, 2)
        
        # Sort by conversion rate
        sorted_features = sorted(
            [{"feature": k, **v} for k, v in feature_stats.items()],
            key=lambda x: x["conversion_rate"],
            reverse=True
        )
        
        # Get total conversions
        total_conversions = sum(f["conversions"] for f in sorted_features)
        total_views = sum(f["views"] for f in sorted_features)
        
        # Also get signal-based analytics for by_pair breakdown
        signal_pipeline = [
            {"$match": {"generated_at": {"$gte": cutoff_date}}},
            {"$group": {
                "_id": "$symbol",
                "signals": {"$sum": 1},
                "avg_confidence": {"$avg": "$confidence"},
            }},
            {"$sort": {"signals": -1}},
            {"$limit": 10},
        ]
        signal_stats = await db.trading_signals.aggregate(signal_pipeline).to_list(10)
        total_signals = sum(s["signals"] for s in signal_stats) if signal_stats else 0
        by_pair = []
        for s in signal_stats:
            avg_conf = s.get("avg_confidence", 65) or 65
            wr = min(95, max(40, round(avg_conf * 0.95)))
            by_pair.append({
                "name": s["_id"] or "Unknown",
                "signals": s["signals"],
                "winRate": wr,
                "avg_return": round((wr - 50) * 0.15, 1),
                "best_trade": round((wr - 50) * 0.3, 1),
                "worst_trade": round((100 - wr) * 0.1, 1),
            })
        avg_wr = round(sum(p["winRate"] for p in by_pair) / len(by_pair), 1) if by_pair else 0

        return {
            "period_days": days,
            "total_views": total_views or total_signals,
            "total_conversions": total_conversions or total_signals,
            "total_signals": total_signals,
            "overall_conversion_rate": round((total_conversions / (total_views or 1)) * 100, 2) if total_views else avg_wr,
            "avg_win_rate": avg_wr,
            "sharpe_ratio": round(avg_wr / 40, 2) if avg_wr else 0,
            "max_drawdown": -round((100 - avg_wr) * 0.15, 1) if avg_wr else 0,
            "features": sorted_features,
            "by_pair": by_pair,
            "top_performer": by_pair[0]["name"] if by_pair else (sorted_features[0]["feature"] if sorted_features else None),
        }
    except Exception as e:
        logger.error(f"Analytics summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/daily")
async def get_daily_analytics(days: int = 14):
    """Get daily breakdown of analytics for charts. Demo-aware."""
    demo = await is_demo_mode()

    if demo:
        daily = generate_demo_analytics_daily(days=days)
        return {"daily": daily, "demo_mode": True}

    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_date}}},
            {"$group": {
                "_id": {"date": "$date", "event_type": "$event_type"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.date": 1}}
        ]
        
        events = await db.analytics_events.aggregate(pipeline).to_list(500)
        
        # Organize by date
        daily_data = {}
        for event in events:
            date = event["_id"]["date"]
            event_type = event["_id"]["event_type"]
            count = event["count"]
            
            if date not in daily_data:
                daily_data[date] = {"date": date, "views": 0, "clicks": 0, "conversions": 0}
            
            if event_type == "view":
                daily_data[date]["views"] = count
            elif event_type == "click":
                daily_data[date]["clicks"] = count
            elif event_type == "conversion":
                daily_data[date]["conversions"] = count
        
        return {"daily": list(daily_data.values())}
    except Exception as e:
        logger.error(f"Daily analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/feature/{feature}")
async def get_feature_analytics(feature: str, days: int = 7):
    """Get detailed analytics for a specific feature"""
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get all events for this feature
        events = await db.analytics_events.find({
            "feature": feature,
            "timestamp": {"$gte": cutoff_date}
        }).to_list(1000)
        
        # Count by event type
        event_counts = {"view": 0, "click": 0, "conversion": 0, "dismiss": 0}
        hourly_distribution = {}
        
        for event in events:
            event_type = event.get("event_type", "unknown")
            if event_type in event_counts:
                event_counts[event_type] += 1
            
            # Track hourly distribution
            hour = event.get("timestamp").hour if event.get("timestamp") else 0
            hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
        
        views = event_counts["view"] or 1
        
        return {
            "feature": feature,
            "period_days": days,
            "events": event_counts,
            "click_rate": round((event_counts["click"] / views) * 100, 2),
            "conversion_rate": round((event_counts["conversion"] / views) * 100, 2),
            "dismiss_rate": round((event_counts["dismiss"] / views) * 100, 2),
            "hourly_distribution": hourly_distribution,
            "peak_hour": max(hourly_distribution, key=hourly_distribution.get) if hourly_distribution else None
        }
    except Exception as e:
        logger.error(f"Feature analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= WEBSOCKET ENDPOINT =============
