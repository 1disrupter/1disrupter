"""
AlphaAI Analytics & A/B Testing Routes
Conversion analytics, A/B testing, and campaign tracking.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid
from database import db, logger

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

@router.get("/analytics/summary")
async def get_analytics_summary(days: int = 7):
    """Get summary of conversion analytics for the last N days"""
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Aggregate events by feature and type
        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_date}}},
            {"$group": {
                "_id": {"feature": "$feature", "event_type": "$event_type"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        events = await db.analytics_events.aggregate(pipeline).to_list(100)
        
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
        
        return {
            "period_days": days,
            "total_views": total_views,
            "total_conversions": total_conversions,
            "overall_conversion_rate": round((total_conversions / (total_views or 1)) * 100, 2),
            "features": sorted_features,
            "top_performer": sorted_features[0]["feature"] if sorted_features else None
        }
    except Exception as e:
        logger.error(f"Analytics summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/daily")
async def get_daily_analytics(days: int = 14):
    """Get daily breakdown of analytics for charts"""
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
