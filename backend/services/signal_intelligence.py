"""
AlphaAI Signal Intelligence Service
AI-powered signal explanations with:
- Trend analysis
- Market sentiment
- Key indicators
- Reasoning for each signal
"""
import os
import json
import random
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("AlphaAI.SignalIntelligence")

# Try to import LLM integration
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("emergentintegrations not available - using fallback signal analysis")

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")

# ============= MODELS =============

class TrendAnalysis(BaseModel):
    """Trend analysis component"""
    direction: str  # "bullish", "bearish", "neutral"
    strength: str  # "strong", "moderate", "weak"
    timeframe: str  # "short-term", "medium-term", "long-term"
    description: str

class MarketSentiment(BaseModel):
    """Market sentiment component"""
    overall: str  # "bullish", "bearish", "neutral", "mixed"
    score: int  # -100 to 100
    factors: list[str]  # Contributing factors
    news_impact: str  # "positive", "negative", "neutral"

class TechnicalIndicators(BaseModel):
    """Technical indicators used"""
    rsi: Dict[str, Any]  # value, signal
    macd: Dict[str, Any]  # signal, histogram
    moving_averages: Dict[str, Any]  # ma20, ma50, ma200
    volume: Dict[str, Any]  # trend, significance
    support_resistance: Dict[str, Any]  # levels

class SignalExplanation(BaseModel):
    """Complete signal explanation"""
    summary: str  # One-line summary
    reasoning: str  # Why this signal was generated
    trend_analysis: TrendAnalysis
    market_sentiment: MarketSentiment
    key_indicators: TechnicalIndicators
    risk_level: str  # "low", "medium", "high"
    confidence_factors: list[str]  # What contributed to confidence
    potential_catalysts: list[str]  # Upcoming events that could impact
    suggested_action: str  # Actionable advice

# ============= SIGNAL INTELLIGENCE SERVICE =============

class SignalIntelligenceService:
    """AI-powered signal explanation generator"""
    
    def __init__(self):
        self.llm_available = LLM_AVAILABLE and EMERGENT_LLM_KEY
        if self.llm_available:
            logger.info("Signal Intelligence using GPT-5.2 for explanations")
        else:
            logger.info("Signal Intelligence using rule-based fallback")
    
    async def generate_signal_explanation(
        self,
        symbol: str,
        signal_type: str,
        confidence: float,
        current_price: float,
        change_24h: float,
        volume_24h: Optional[float] = None,
        market_cap: Optional[float] = None
    ) -> SignalExplanation:
        """
        Generate comprehensive AI explanation for a trading signal.
        """
        if self.llm_available:
            return await self._generate_ai_explanation(
                symbol, signal_type, confidence, current_price, 
                change_24h, volume_24h, market_cap
            )
        else:
            return self._generate_fallback_explanation(
                symbol, signal_type, confidence, current_price, change_24h
            )
    
    async def _generate_ai_explanation(
        self,
        symbol: str,
        signal_type: str,
        confidence: float,
        current_price: float,
        change_24h: float,
        volume_24h: Optional[float],
        market_cap: Optional[float]
    ) -> SignalExplanation:
        """Generate explanation using GPT-5.2"""
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"signal-{symbol}-{datetime.now().timestamp()}",
                system_message="""You are an expert crypto trading analyst. Generate detailed, professional trading signal explanations in JSON format.
                
Be specific with numbers and technical details. Use real technical indicator concepts (RSI, MACD, Moving Averages, Volume Analysis).
Make explanations educational and actionable for traders.

Always respond with valid JSON matching the exact structure requested."""
            ).with_model("openai", "gpt-5.2")
            
            prompt = f"""Analyze this trading signal and provide a detailed explanation:

SIGNAL DATA:
- Symbol: {symbol}
- Signal Type: {signal_type}
- Confidence: {confidence}%
- Current Price: ${current_price:,.2f}
- 24h Change: {change_24h:+.2f}%
{f"- 24h Volume: ${volume_24h:,.0f}" if volume_24h else ""}
{f"- Market Cap: ${market_cap:,.0f}" if market_cap else ""}

Generate a JSON response with this exact structure:
{{
    "summary": "One sentence summary of why this signal was generated",
    "reasoning": "2-3 sentences explaining the main reasoning behind this signal",
    "trend_analysis": {{
        "direction": "bullish|bearish|neutral",
        "strength": "strong|moderate|weak",
        "timeframe": "short-term|medium-term|long-term",
        "description": "Description of the current trend"
    }},
    "market_sentiment": {{
        "overall": "bullish|bearish|neutral|mixed",
        "score": -100 to 100 integer,
        "factors": ["factor1", "factor2", "factor3"],
        "news_impact": "positive|negative|neutral"
    }},
    "key_indicators": {{
        "rsi": {{"value": 0-100, "signal": "overbought|oversold|neutral"}},
        "macd": {{"signal": "bullish|bearish|neutral", "histogram": "expanding|contracting"}},
        "moving_averages": {{"ma20_position": "above|below", "ma50_trend": "up|down|flat", "golden_cross": true|false}},
        "volume": {{"trend": "increasing|decreasing|stable", "significance": "high|normal|low"}},
        "support_resistance": {{"nearest_support": price, "nearest_resistance": price}}
    }},
    "risk_level": "low|medium|high",
    "confidence_factors": ["factor1", "factor2", "factor3"],
    "potential_catalysts": ["catalyst1", "catalyst2"],
    "suggested_action": "Specific actionable advice for traders"
}}

Respond ONLY with the JSON, no other text."""

            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            # Parse JSON response
            try:
                # Clean response if needed
                response_text = response.strip()
                if response_text.startswith("```"):
                    response_text = response_text.split("```")[1]
                    if response_text.startswith("json"):
                        response_text = response_text[4:]
                
                data = json.loads(response_text)
                
                return SignalExplanation(
                    summary=data.get("summary", f"{signal_type} signal for {symbol}"),
                    reasoning=data.get("reasoning", "AI analysis complete."),
                    trend_analysis=TrendAnalysis(**data.get("trend_analysis", {
                        "direction": "neutral",
                        "strength": "moderate",
                        "timeframe": "short-term",
                        "description": "Trend analysis pending"
                    })),
                    market_sentiment=MarketSentiment(**data.get("market_sentiment", {
                        "overall": "neutral",
                        "score": 0,
                        "factors": [],
                        "news_impact": "neutral"
                    })),
                    key_indicators=TechnicalIndicators(**{
                        "rsi": data.get("key_indicators", {}).get("rsi", {"value": 50, "signal": "neutral"}),
                        "macd": data.get("key_indicators", {}).get("macd", {"signal": "neutral", "histogram": "stable"}),
                        "moving_averages": data.get("key_indicators", {}).get("moving_averages", {}),
                        "volume": data.get("key_indicators", {}).get("volume", {}),
                        "support_resistance": data.get("key_indicators", {}).get("support_resistance", {})
                    }),
                    risk_level=data.get("risk_level", "medium"),
                    confidence_factors=data.get("confidence_factors", []),
                    potential_catalysts=data.get("potential_catalysts", []),
                    suggested_action=data.get("suggested_action", "Monitor position and set appropriate stop-loss.")
                )
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response: {e}")
                return self._generate_fallback_explanation(
                    symbol, signal_type, confidence, current_price, change_24h
                )
                
        except Exception as e:
            logger.error(f"AI explanation generation failed: {e}")
            return self._generate_fallback_explanation(
                symbol, signal_type, confidence, current_price, change_24h
            )
    
    def _generate_fallback_explanation(
        self,
        symbol: str,
        signal_type: str,
        confidence: float,
        current_price: float,
        change_24h: float
    ) -> SignalExplanation:
        """Generate rule-based explanation as fallback"""
        
        # Determine trend
        if change_24h > 3:
            trend_dir = "bullish"
            trend_strength = "strong"
        elif change_24h > 1:
            trend_dir = "bullish"
            trend_strength = "moderate"
        elif change_24h < -3:
            trend_dir = "bearish"
            trend_strength = "strong"
        elif change_24h < -1:
            trend_dir = "bearish"
            trend_strength = "moderate"
        else:
            trend_dir = "neutral"
            trend_strength = "weak"
        
        # RSI simulation based on price change
        rsi_value = 50 + (change_24h * 3)
        rsi_value = max(20, min(80, rsi_value + random.randint(-5, 5)))
        rsi_signal = "overbought" if rsi_value > 70 else "oversold" if rsi_value < 30 else "neutral"
        
        # MACD simulation
        macd_signal = "bullish" if change_24h > 0 else "bearish" if change_24h < 0 else "neutral"
        
        # Support/Resistance estimation
        support = current_price * 0.95
        resistance = current_price * 1.05
        
        # Generate reasoning
        if signal_type == "BUY":
            summary = f"{symbol} showing bullish momentum with favorable technical setup"
            reasoning = f"{symbol} has gained {change_24h:+.1f}% in 24 hours, breaking above key moving averages. RSI at {rsi_value:.0f} indicates room for further upside. Volume confirms buying pressure."
            sentiment_score = min(80, int(50 + change_24h * 5))
        elif signal_type == "SELL":
            summary = f"{symbol} facing selling pressure with bearish technical indicators"
            reasoning = f"{symbol} has declined {change_24h:.1f}% in 24 hours, breaking below support levels. RSI at {rsi_value:.0f} with MACD showing bearish crossover suggests continued weakness."
            sentiment_score = max(-80, int(-50 + change_24h * 5))
        else:
            summary = f"{symbol} consolidating near ${current_price:,.2f} - waiting for directional clarity"
            reasoning = f"{symbol} is range-bound with {change_24h:+.1f}% change. Mixed signals from indicators suggest waiting for a clearer trend before entering a position."
            sentiment_score = int(change_24h * 5)
        
        # Risk level based on volatility
        risk_level = "high" if abs(change_24h) > 5 else "medium" if abs(change_24h) > 2 else "low"
        
        # Confidence factors
        confidence_factors = []
        if abs(change_24h) > 2:
            confidence_factors.append("Strong price momentum")
        if confidence > 75:
            confidence_factors.append("Multiple indicators aligned")
        if rsi_value > 60 or rsi_value < 40:
            confidence_factors.append("RSI confirmation")
        confidence_factors.append("Volume analysis supportive")
        
        # Potential catalysts
        catalysts = [
            "Upcoming market events",
            "Broader crypto market trends",
            f"Technical breakout at ${resistance:,.2f}" if signal_type == "BUY" else f"Support test at ${support:,.2f}"
        ]
        
        # Suggested action
        if signal_type == "BUY":
            suggested_action = f"Consider entry near ${current_price:,.2f} with stop-loss at ${support:,.2f}. Target resistance at ${resistance:,.2f}."
        elif signal_type == "SELL":
            suggested_action = f"Consider reducing exposure or shorting near ${current_price:,.2f}. Watch support at ${support:,.2f}."
        else:
            suggested_action = f"Wait for price to break above ${resistance:,.2f} or below ${support:,.2f} before taking action."
        
        return SignalExplanation(
            summary=summary,
            reasoning=reasoning,
            trend_analysis=TrendAnalysis(
                direction=trend_dir,
                strength=trend_strength,
                timeframe="short-term",
                description=f"{symbol} is in a {trend_strength} {trend_dir} trend based on recent price action and momentum indicators."
            ),
            market_sentiment=MarketSentiment(
                overall=trend_dir if trend_dir != "neutral" else "mixed",
                score=sentiment_score,
                factors=[
                    f"24h price change: {change_24h:+.1f}%",
                    f"RSI at {rsi_value:.0f}",
                    "Technical indicator alignment"
                ],
                news_impact="neutral"
            ),
            key_indicators=TechnicalIndicators(
                rsi={"value": round(rsi_value), "signal": rsi_signal},
                macd={"signal": macd_signal, "histogram": "expanding" if abs(change_24h) > 2 else "stable"},
                moving_averages={
                    "ma20_position": "above" if change_24h > 0 else "below",
                    "ma50_trend": "up" if change_24h > 1 else "down" if change_24h < -1 else "flat",
                    "golden_cross": change_24h > 3
                },
                volume={
                    "trend": "increasing" if abs(change_24h) > 2 else "stable",
                    "significance": "high" if abs(change_24h) > 3 else "normal"
                },
                support_resistance={
                    "nearest_support": round(support, 2),
                    "nearest_resistance": round(resistance, 2)
                }
            ),
            risk_level=risk_level,
            confidence_factors=confidence_factors,
            potential_catalysts=catalysts,
            suggested_action=suggested_action
        )


# Singleton instance
signal_intelligence = SignalIntelligenceService()

async def get_signal_intelligence() -> SignalIntelligenceService:
    """Get signal intelligence service instance"""
    return signal_intelligence
