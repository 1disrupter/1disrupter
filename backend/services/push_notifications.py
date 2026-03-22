"""
AlphaAI Push Notification Service
Backend hooks for push notifications - service agnostic
Supports: Expo, FCM, APNs (via configuration)
"""
import os
import asyncio
import logging
import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger("AlphaAI.PushNotifications")

# MongoDB connection
db = None

def init_db(database):
    global db
    db = database

class NotificationType(str, Enum):
    SIGNAL_ALERT = "signal_alert"
    TRADE_EXECUTED = "trade_executed"
    TRADE_CLOSED = "trade_closed"
    PRICE_ALERT = "price_alert"
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_REPORT = "weekly_report"
    REFERRAL_SIGNUP = "referral_signup"
    REFERRAL_CONVERSION = "referral_conversion"
    PRO_UPGRADE = "pro_upgrade"
    SYSTEM = "system"

class PushNotificationService:
    """
    Push notification service supporting multiple providers.
    Currently implements Expo push notifications.
    Easy to extend for FCM, APNs, OneSignal.
    """
    
    EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"
    
    def __init__(self):
        self.expo_access_token = os.environ.get("EXPO_ACCESS_TOKEN")
        self.enabled = True
        logger.info("Push notification service initialized")
    
    async def send_to_user(
        self,
        user_id: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        notification_type: NotificationType = NotificationType.SYSTEM,
        badge: Optional[int] = None,
        sound: str = "default"
    ) -> Dict[str, Any]:
        """
        Send push notification to all devices of a user.
        """
        if not self.enabled:
            return {"success": False, "reason": "Push notifications disabled"}
        
        # Check user preferences
        prefs = await db.notification_preferences.find_one({"user_id": user_id})
        if prefs:
            if not prefs.get("push_enabled", True):
                return {"success": False, "reason": "User disabled push notifications"}
            
            # Check specific notification type preferences
            type_pref_map = {
                NotificationType.SIGNAL_ALERT: "signal_alerts",
                NotificationType.TRADE_EXECUTED: "trade_confirmations",
                NotificationType.TRADE_CLOSED: "trade_confirmations",
                NotificationType.PRICE_ALERT: "price_alerts",
                NotificationType.DAILY_SUMMARY: "daily_summary",
                NotificationType.WEEKLY_REPORT: "weekly_report",
            }
            
            pref_key = type_pref_map.get(notification_type)
            if pref_key and not prefs.get(pref_key, True):
                return {"success": False, "reason": f"User disabled {notification_type}"}
            
            # Check quiet hours
            quiet = prefs.get("quiet_hours", {})
            if quiet.get("enabled"):
                # Simple quiet hours check (would need proper timezone handling in production)
                now_hour = datetime.now(timezone.utc).hour
                start_hour = int(quiet.get("start", "22:00").split(":")[0])
                end_hour = int(quiet.get("end", "08:00").split(":")[0])
                
                if start_hour <= now_hour or now_hour < end_hour:
                    # Store for later delivery
                    await self._queue_notification(user_id, title, body, data, notification_type)
                    return {"success": True, "queued": True, "reason": "Quiet hours"}
        
        # Get user's devices
        devices = await db.user_devices.find({
            "user_id": user_id,
            "is_active": True
        }).to_list(10)
        
        if not devices:
            return {"success": False, "reason": "No registered devices"}
        
        # Send to each device
        results = []
        for device in devices:
            result = await self._send_to_device(
                push_token=device["push_token"],
                platform=device["platform"],
                title=title,
                body=body,
                data=data,
                badge=badge,
                sound=sound
            )
            results.append({
                "device_id": device["device_id"],
                "platform": device["platform"],
                **result
            })
        
        # Log notification
        await self._log_notification(user_id, title, body, notification_type, results)
        
        successes = sum(1 for r in results if r.get("success"))
        return {
            "success": successes > 0,
            "sent_to": successes,
            "total_devices": len(devices),
            "results": results
        }
    
    async def _send_to_device(
        self,
        push_token: str,
        platform: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        badge: Optional[int] = None,
        sound: str = "default"
    ) -> Dict[str, Any]:
        """Send to a specific device based on platform"""
        
        if platform == "expo" or push_token.startswith("ExponentPushToken"):
            return await self._send_expo(push_token, title, body, data, badge, sound)
        elif platform == "ios":
            # Would implement APNs here
            return await self._send_expo(push_token, title, body, data, badge, sound)
        elif platform == "android":
            # Would implement FCM here
            return await self._send_expo(push_token, title, body, data, badge, sound)
        else:
            # Default to Expo format
            return await self._send_expo(push_token, title, body, data, badge, sound)
    
    async def _send_expo(
        self,
        push_token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        badge: Optional[int] = None,
        sound: str = "default"
    ) -> Dict[str, Any]:
        """Send via Expo Push API"""
        
        message = {
            "to": push_token,
            "title": title,
            "body": body,
            "sound": sound,
            "priority": "high"
        }
        
        if data:
            message["data"] = data
        if badge is not None:
            message["badge"] = badge
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.expo_access_token:
            headers["Authorization"] = f"Bearer {self.expo_access_token}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.EXPO_PUSH_URL,
                    json=message,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ticket = result.get("data", {})
                    
                    if ticket.get("status") == "ok":
                        return {"success": True, "ticket_id": ticket.get("id")}
                    else:
                        error = ticket.get("details", {}).get("error", "Unknown error")
                        
                        # Handle invalid tokens
                        if error in ["DeviceNotRegistered", "InvalidCredentials"]:
                            await self._mark_device_inactive(push_token)
                        
                        return {"success": False, "error": error}
                else:
                    return {"success": False, "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Expo push error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _mark_device_inactive(self, push_token: str):
        """Mark device as inactive when token is invalid"""
        await db.user_devices.update_many(
            {"push_token": push_token},
            {"$set": {"is_active": False}}
        )
        logger.info(f"Marked device inactive: {push_token[:20]}...")
    
    async def _queue_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        data: Optional[Dict],
        notification_type: NotificationType
    ):
        """Queue notification for later delivery (quiet hours)"""
        await db.notification_queue.insert_one({
            "user_id": user_id,
            "title": title,
            "body": body,
            "data": data,
            "type": notification_type,
            "created_at": datetime.now(timezone.utc),
            "status": "pending"
        })
    
    async def _log_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        notification_type: NotificationType,
        results: List[Dict]
    ):
        """Log notification for history"""
        await db.notification_history.insert_one({
            "user_id": user_id,
            "title": title,
            "body": body,
            "type": notification_type,
            "results": results,
            "sent_at": datetime.now(timezone.utc)
        })
    
    # ============= NOTIFICATION TEMPLATES =============
    
    async def send_signal_alert(
        self,
        user_id: str,
        symbol: str,
        signal_type: str,
        confidence: int,
        price: float
    ):
        """Send new trading signal alert"""
        emoji = "🟢" if signal_type == "BUY" else "🔴"
        return await self.send_to_user(
            user_id=user_id,
            title=f"{emoji} {signal_type} Signal: {symbol}",
            body=f"{confidence}% confidence at ${price:,.2f}",
            data={
                "type": "signal",
                "symbol": symbol,
                "signal_type": signal_type,
                "screen": "signals"
            },
            notification_type=NotificationType.SIGNAL_ALERT,
            sound="default"
        )
    
    async def send_trade_executed(
        self,
        user_id: str,
        symbol: str,
        side: str,
        amount: float,
        price: float
    ):
        """Send trade execution confirmation"""
        emoji = "📈" if side == "BUY" else "📉"
        return await self.send_to_user(
            user_id=user_id,
            title=f"{emoji} Trade Executed",
            body=f"{side} {amount} {symbol} at ${price:,.2f}",
            data={
                "type": "trade",
                "symbol": symbol,
                "side": side,
                "screen": "portfolio"
            },
            notification_type=NotificationType.TRADE_EXECUTED
        )
    
    async def send_trade_closed(
        self,
        user_id: str,
        symbol: str,
        pnl: float,
        pnl_percent: float
    ):
        """Send trade closure notification"""
        emoji = "✅" if pnl >= 0 else "❌"
        sign = "+" if pnl >= 0 else ""
        return await self.send_to_user(
            user_id=user_id,
            title=f"{emoji} Trade Closed: {symbol}",
            body=f"P&L: {sign}${pnl:,.2f} ({sign}{pnl_percent:.1f}%)",
            data={
                "type": "trade_closed",
                "symbol": symbol,
                "pnl": pnl,
                "screen": "portfolio"
            },
            notification_type=NotificationType.TRADE_CLOSED
        )
    
    async def send_price_alert(
        self,
        user_id: str,
        symbol: str,
        current_price: float,
        alert_price: float,
        direction: str  # "above" or "below"
    ):
        """Send price alert"""
        emoji = "⬆️" if direction == "above" else "⬇️"
        return await self.send_to_user(
            user_id=user_id,
            title=f"{emoji} Price Alert: {symbol}",
            body=f"Now ${current_price:,.2f} ({direction} ${alert_price:,.2f})",
            data={
                "type": "price_alert",
                "symbol": symbol,
                "price": current_price,
                "screen": "dashboard"
            },
            notification_type=NotificationType.PRICE_ALERT
        )
    
    async def send_referral_signup(self, user_id: str, referee_email: str):
        """Send referral signup notification"""
        masked_email = referee_email[0] + "***@" + referee_email.split("@")[1][:3] + "***"
        return await self.send_to_user(
            user_id=user_id,
            title="🎉 New Referral Signup!",
            body=f"{masked_email} joined using your link",
            data={
                "type": "referral",
                "screen": "referrals"
            },
            notification_type=NotificationType.REFERRAL_SIGNUP
        )
    
    async def send_referral_conversion(
        self,
        user_id: str,
        commission: float,
        plan: str
    ):
        """Send referral conversion notification"""
        return await self.send_to_user(
            user_id=user_id,
            title="💰 Referral Converted!",
            body=f"You earned ${commission:.2f} commission ({plan})",
            data={
                "type": "referral_conversion",
                "commission": commission,
                "screen": "referrals"
            },
            notification_type=NotificationType.REFERRAL_CONVERSION
        )
    
    async def send_daily_summary(
        self,
        user_id: str,
        trades: int,
        pnl: float,
        win_rate: float
    ):
        """Send daily trading summary"""
        emoji = "📊"
        sign = "+" if pnl >= 0 else ""
        return await self.send_to_user(
            user_id=user_id,
            title=f"{emoji} Daily Summary",
            body=f"{trades} trades | {sign}${pnl:.2f} P&L | {win_rate:.0f}% win rate",
            data={
                "type": "daily_summary",
                "screen": "dashboard"
            },
            notification_type=NotificationType.DAILY_SUMMARY
        )
    
    async def send_pro_upgrade(self, user_id: str, plan: str):
        """Send Pro upgrade confirmation"""
        return await self.send_to_user(
            user_id=user_id,
            title="🎊 Welcome to Pro!",
            body=f"You now have access to real-time signals ({plan})",
            data={
                "type": "pro_upgrade",
                "plan": plan,
                "screen": "dashboard"
            },
            notification_type=NotificationType.PRO_UPGRADE
        )

# Singleton instance
push_service = PushNotificationService()

async def get_push_service() -> PushNotificationService:
    """Get push notification service instance"""
    return push_service
