"""
AlphaAI Signal Service
Tiered signal generation with free (15-min delay) and pro (real-time) tiers.
"""
import asyncio
import random
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from database import db, EMERGENT_LLM_KEY
from services.signal_intelligence import signal_intelligence
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger("AlphaAI")

class TradingSignal(BaseModel):
    """Trading signal with timestamp for tier-based delivery"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    signal_type: str  # BUY, SELL, HOLD
    confidence: float  # 0-100
    price_at_signal: float
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    analysis: str = ""
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    is_priority: bool = False  # Priority signals for Pro/Elite
    # AI Signal Intelligence fields
    explanation: Optional[str] = None  # Summary explanation
    reasoning: Optional[str] = None  # Why this signal was generated
    trend_analysis: Optional[Dict[str, Any]] = None  # Trend direction, strength, timeframe
    market_sentiment: Optional[Dict[str, Any]] = None  # Overall sentiment, score, factors
    key_indicators: Optional[Dict[str, Any]] = None  # RSI, MACD, MAs, Volume, S/R
    risk_level: Optional[str] = None  # low, medium, high
    confidence_factors: Optional[List[str]] = None  # What contributed to confidence
    potential_catalysts: Optional[List[str]] = None  # Upcoming events
    suggested_action: Optional[str] = None  # Actionable advice

# Signal delay configuration
SIGNAL_DELAYS = {
    "free": 15 * 60,      # 15 minutes in seconds
    "pro": 0,             # Real-time
    "elite": 0            # Real-time
}

SIGNAL_REFRESH_RATES = {
    "free": 300,          # 5 minutes refresh
    "pro": 60,            # 1 minute refresh
    "elite": 30           # 30 seconds refresh
}

class SignalService:
    """Manages tiered signal generation and delivery"""
    
    def __init__(self):
        self.last_generation = None
        self.current_signals = {}
        self.signal_history = []
    
    async def generate_signals(self, force: bool = False) -> List[Dict]:
        """Generate fresh trading signals using AI and market data"""
        try:
            # Fetch live prices
            prices = await self._fetch_live_prices()
            if not prices:
                return []
            
            signals = []
            for asset in ["BTC", "ETH", "SOL"]:
                price_data = next((p for p in prices if p.get("symbol") == asset), None)
                if not price_data:
                    continue
                
                current_price = price_data.get("price", 0)
                change_24h = price_data.get("change_24h", 0)
                volume_24h = price_data.get("volume_24h")
                market_cap = price_data.get("market_cap")
                
                # Generate basic signal based on market data
                signal_type, confidence, analysis = await self._analyze_asset(asset, current_price, change_24h)
                
                # Generate AI-powered explanation using Signal Intelligence Service
                try:
                    ai_explanation = await signal_intelligence.generate_signal_explanation(
                        symbol=asset,
                        signal_type=signal_type,
                        confidence=confidence,
                        current_price=current_price,
                        change_24h=change_24h,
                        volume_24h=volume_24h,
                        market_cap=market_cap
                    )
                    
                    # Create signal with AI explanations
                    signal = TradingSignal(
                        symbol=asset,
                        signal_type=signal_type,
                        confidence=confidence,
                        price_at_signal=current_price,
                        analysis=analysis,
                        generated_at=datetime.now(timezone.utc),
                        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
                        is_priority=False,
                        # AI Signal Intelligence fields
                        explanation=ai_explanation.summary,
                        reasoning=ai_explanation.reasoning,
                        trend_analysis=ai_explanation.trend_analysis.model_dump() if ai_explanation.trend_analysis else None,
                        market_sentiment=ai_explanation.market_sentiment.model_dump() if ai_explanation.market_sentiment else None,
                        key_indicators=ai_explanation.key_indicators.model_dump() if ai_explanation.key_indicators else None,
                        risk_level=ai_explanation.risk_level,
                        confidence_factors=ai_explanation.confidence_factors,
                        potential_catalysts=ai_explanation.potential_catalysts,
                        suggested_action=ai_explanation.suggested_action
                    )
                    logger.info(f"Generated AI explanation for {asset}: {ai_explanation.summary[:50]}...")
                except Exception as ai_err:
                    logger.warning(f"AI explanation failed for {asset}, using basic signal: {ai_err}")
                    signal = TradingSignal(
                        symbol=asset,
                        signal_type=signal_type,
                        confidence=confidence,
                        price_at_signal=current_price,
                        analysis=analysis,
                        generated_at=datetime.now(timezone.utc),
                        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
                        is_priority=False
                    )
                
                signals.append(signal)
                
                # Store in database with AI explanations
                signal_doc = {
                    "id": signal.id,
                    "symbol": signal.symbol,
                    "signal_type": signal.signal_type,
                    "confidence": signal.confidence,
                    "price_at_signal": signal.price_at_signal,
                    "analysis": signal.analysis,
                    "generated_at": signal.generated_at,
                    "expires_at": signal.expires_at,
                    "is_priority": signal.is_priority,
                    # AI explanation fields
                    "explanation": signal.explanation,
                    "reasoning": signal.reasoning,
                    "trend_analysis": signal.trend_analysis,
                    "market_sentiment": signal.market_sentiment,
                    "key_indicators": signal.key_indicators,
                    "risk_level": signal.risk_level,
                    "confidence_factors": signal.confidence_factors,
                    "potential_catalysts": signal.potential_catalysts,
                    "suggested_action": signal.suggested_action
                }
                await db.trading_signals.insert_one(signal_doc)
                
                # Send push notifications for high-confidence signals to Pro/Elite users
                if signal.confidence >= 75 and signal.signal_type in ["BUY", "SELL"]:
                    try:
                        # Import here to avoid circular imports
                        from services.push_notifications import push_service
                        await push_service.notify_pro_users_high_confidence_signal(
                            symbol=signal.symbol,
                            signal_type=signal.signal_type,
                            confidence=signal.confidence,
                            price=signal.price_at_signal,
                            explanation=signal.explanation,
                            suggested_action=signal.suggested_action,
                            risk_level=signal.risk_level
                        )
                        logger.info(f"Push notification sent for high-confidence {signal.signal_type} signal on {signal.symbol}")
                    except Exception as push_err:
                        logger.warning(f"Push notification failed for {signal.symbol}: {push_err}")
            
            self.last_generation = datetime.now(timezone.utc)
            logger.info(f"Generated {len(signals)} new trading signals with AI intelligence")
            return signals
            
        except Exception as e:
            logger.error(f"Signal generation error: {str(e)}")
            return []
    
    async def _fetch_live_prices(self) -> List[Dict]:
        """Fetch live prices from Kraken"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.kraken.com/0/public/Ticker", params={
                    "pair": "XBTUSD,ETHUSD,SOLUSD"
                })
                data = response.json()
                
                if data.get("error"):
                    return []
                
                result = data.get("result", {})
                prices = []
                
                symbol_map = {"XXBTZUSD": "BTC", "XETHZUSD": "ETH", "SOLUSD": "SOL"}
                for kraken_symbol, asset in symbol_map.items():
                    if kraken_symbol in result:
                        ticker = result[kraken_symbol]
                        price = float(ticker["c"][0])
                        open_price = float(ticker["o"])
                        change = ((price - open_price) / open_price) * 100 if open_price else 0
                        prices.append({
                            "symbol": asset,
                            "price": price,
                            "change_24h": round(change, 2)
                        })
                
                return prices
        except Exception as e:
            logger.error(f"Price fetch error: {str(e)}")
            return []
    
    async def _analyze_asset(self, symbol: str, price: float, change_24h: float) -> tuple:
        """Analyze asset and generate signal using AI"""
        try:
            # Simple rule-based signal with some randomization for demo
            # In production, this would use more sophisticated AI analysis
            
            if change_24h > 3:
                signal_type = "BUY"
                confidence = min(90, 70 + change_24h * 2)
                analysis = f"{symbol} showing strong bullish momentum with +{change_24h:.1f}% gain."
            elif change_24h < -3:
                signal_type = "SELL"
                confidence = min(90, 70 + abs(change_24h) * 2)
                analysis = f"{symbol} showing bearish pressure with {change_24h:.1f}% decline."
            elif change_24h > 1:
                signal_type = "BUY"
                confidence = 60 + change_24h * 5
                analysis = f"{symbol} showing moderate bullish trend at ${price:,.2f}."
            elif change_24h < -1:
                signal_type = "SELL"
                confidence = 60 + abs(change_24h) * 5
                analysis = f"{symbol} facing selling pressure. Consider reducing exposure."
            else:
                signal_type = "HOLD"
                confidence = 50 + random.randint(0, 20)
                analysis = f"{symbol} consolidating near ${price:,.2f}. Wait for clearer direction."
            
            # Add some realistic variance
            confidence = min(95, max(45, confidence + random.randint(-5, 5)))
            
            return signal_type, round(confidence, 1), analysis
            
        except Exception as e:
            logger.error(f"Analysis error for {symbol}: {str(e)}")
            return "HOLD", 50.0, f"Unable to analyze {symbol} at this time."
    
    async def get_signals_for_tier(self, tier: str = "free", wallet_address: Optional[str] = None) -> List[Dict]:
        """Get signals appropriate for the user's subscription tier"""
        
        # Determine actual tier from database if wallet provided
        actual_tier = tier
        if wallet_address:
            investor = await db.investors.find_one({"wallet_address": wallet_address})
            if investor:
                if investor.get("is_elite"):
                    actual_tier = "elite"
                elif investor.get("is_pro"):
                    actual_tier = "pro"
        
        delay_seconds = SIGNAL_DELAYS.get(actual_tier, SIGNAL_DELAYS["free"])
        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=delay_seconds)
        
        # For free users, only return signals older than 15 minutes
        if actual_tier == "free":
            query = {"generated_at": {"$lte": cutoff_time}}
        else:
            # Pro/Elite get all signals including the latest
            query = {}
        
        # Get most recent signal per symbol
        pipeline = [
            {"$match": query},
            {"$sort": {"generated_at": -1}},
            {"$group": {
                "_id": "$symbol",
                "latest": {"$first": "$$ROOT"}
            }},
            {"$replaceRoot": {"newRoot": "$latest"}},
            {"$project": {"_id": 0}}
        ]
        
        signals = await db.trading_signals.aggregate(pipeline).to_list(10)
        
        # Add delay info for frontend
        for signal in signals:
            signal["is_delayed"] = actual_tier == "free"
            signal["delay_minutes"] = 15 if actual_tier == "free" else 0
            signal["tier"] = actual_tier
            # Convert datetime to string for JSON
            if isinstance(signal.get("generated_at"), datetime):
                signal["generated_at"] = signal["generated_at"].isoformat()
            if isinstance(signal.get("expires_at"), datetime):
                signal["expires_at"] = signal["expires_at"].isoformat()
        
        return signals
    
    async def get_realtime_signals(self, wallet_address: str) -> List[Dict]:
        """Get real-time signals - Pro/Elite only"""
        # Verify subscription
        investor = await db.investors.find_one({"wallet_address": wallet_address})
        if not investor or not (investor.get("is_pro") or investor.get("is_elite")):
            raise HTTPException(
                status_code=403, 
                detail="Real-time signals require Pro or Elite subscription"
            )
        
        # Get the absolute latest signals
        pipeline = [
            {"$sort": {"generated_at": -1}},
            {"$group": {
                "_id": "$symbol",
                "latest": {"$first": "$$ROOT"}
            }},
            {"$replaceRoot": {"newRoot": "$latest"}},
            {"$project": {"_id": 0}}
        ]
        
        signals = await db.trading_signals.aggregate(pipeline).to_list(10)
        
        for signal in signals:
            signal["is_delayed"] = False
            signal["delay_minutes"] = 0
            signal["tier"] = "pro" if investor.get("is_pro") else "elite"
            if isinstance(signal.get("generated_at"), datetime):
                signal["generated_at"] = signal["generated_at"].isoformat()
            if isinstance(signal.get("expires_at"), datetime):
                signal["expires_at"] = signal["expires_at"].isoformat()
        
        return signals

# Initialize signal service
signal_service = SignalService()

# Background task to generate signals periodically
async def signal_generation_task():
    """Background task to generate signals every minute and broadcast via WebSocket"""
    while True:
        try:
            signals = await signal_service.generate_signals()
            
            # Broadcast new signals to Pro/Elite WebSocket connections
            if signals:
                signal_data = []
                for s in signals:
                    signal_data.append({
                        "symbol": s.symbol,
                        "signal_type": s.signal_type,
                        "confidence": s.confidence,
                        "price": s.price_at_signal,
                        "analysis": s.analysis,
                        "generated_at": s.generated_at.isoformat() if hasattr(s.generated_at, 'isoformat') else str(s.generated_at)
                    })
                
                await ws_manager.broadcast_to_channel("signals", {
                    "type": "signals_update",
                    "data": signal_data,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
        except Exception as e:
            logger.error(f"Signal generation task error: {str(e)}")
        await asyncio.sleep(60)  # Generate new signals every minute

# Background task for price updates (more frequent for WebSocket)
async def price_broadcast_task():
    """Broadcast live prices every 5 seconds to WebSocket connections"""
    while True:
        try:
            prices = await signal_service._fetch_live_prices()
            if prices:
                await ws_manager.broadcast_to_channel("prices", {
                    "type": "price_update",
                    "data": prices,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                # Update order manager with current prices for SL/TP monitoring
                from services.order_manager import order_manager
                price_dict = {p["symbol"]: p["price"] for p in prices if "symbol" in p and "price" in p}
                await order_manager.update_prices(price_dict)
        except Exception as e:
            logger.error(f"Price broadcast error: {str(e)}")
        await asyncio.sleep(5)  # Broadcast prices every 5 seconds for Pro/Elite

signal_service = SignalService()
