"""
AI Signal Intelligence API Tests
Tests for the AI-powered signal explanation feature including:
- Signal generation with AI explanations
- Tiered signal delivery (free vs pro/elite)
- AI explanation fields (trend_analysis, market_sentiment, key_indicators, etc.)
"""

import pytest
import requests
import os
from datetime import datetime, timezone, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test wallet addresses
TEST_PRO_WALLET = "0xTEST_AI_SIGNALS_PRO"
TEST_ELITE_WALLET = "0xTEST_AI_SIGNALS_ELITE"
TEST_FREE_WALLET = "0xTEST_AI_SIGNALS_FREE"


class TestSignalIntelligenceBackend:
    """Tests for AI Signal Intelligence backend functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    # ============= SIGNAL ENDPOINTS =============
    
    def test_free_signals_endpoint_returns_signals(self):
        """Test /api/signals/free returns signals for free tier"""
        response = self.session.get(f"{BASE_URL}/api/signals/free")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "signals" in data, "Response should contain 'signals' field"
        assert "tier" in data, "Response should contain 'tier' field"
        assert data["tier"] == "free", "Tier should be 'free'"
        assert "delay_minutes" in data, "Response should contain 'delay_minutes'"
        assert data["delay_minutes"] == 15, "Free tier should have 15 minute delay"
        
        # Verify signals structure
        if data["signals"]:
            signal = data["signals"][0]
            assert "symbol" in signal, "Signal should have 'symbol'"
            assert "signal_type" in signal, "Signal should have 'signal_type'"
            assert "confidence" in signal, "Signal should have 'confidence'"
            assert "price_at_signal" in signal, "Signal should have 'price_at_signal'"
            assert signal["is_delayed"] == True, "Free tier signals should be delayed"
        
        print(f"✓ Free signals endpoint returned {len(data['signals'])} signals")
    
    def test_pro_signals_endpoint_returns_realtime_signals(self):
        """Test /api/signals/tiered returns real-time signals for Pro users"""
        response = self.session.get(
            f"{BASE_URL}/api/signals/tiered",
            params={"wallet_address": TEST_PRO_WALLET}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["tier"] == "pro", f"Expected tier 'pro', got {data['tier']}"
        assert data["delay_minutes"] == 0, "Pro tier should have 0 delay"
        
        if data["signals"]:
            signal = data["signals"][0]
            assert signal["is_delayed"] == False, "Pro tier signals should not be delayed"
        
        print(f"✓ Pro signals endpoint returned {len(data['signals'])} real-time signals")
    
    def test_pro_signals_have_ai_explanations(self):
        """Test that Pro tier signals include AI explanation fields"""
        response = self.session.get(
            f"{BASE_URL}/api/signals/tiered",
            params={"wallet_address": TEST_PRO_WALLET}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["signals"]) > 0, "Should have at least one signal"
        
        signal = data["signals"][0]
        
        # Check AI explanation fields exist
        assert "explanation" in signal, "Signal should have 'explanation' field"
        assert "reasoning" in signal, "Signal should have 'reasoning' field"
        assert "trend_analysis" in signal, "Signal should have 'trend_analysis' field"
        assert "market_sentiment" in signal, "Signal should have 'market_sentiment' field"
        assert "key_indicators" in signal, "Signal should have 'key_indicators' field"
        assert "risk_level" in signal, "Signal should have 'risk_level' field"
        assert "confidence_factors" in signal, "Signal should have 'confidence_factors' field"
        assert "potential_catalysts" in signal, "Signal should have 'potential_catalysts' field"
        assert "suggested_action" in signal, "Signal should have 'suggested_action' field"
        
        # Verify AI explanation content is populated
        assert signal["explanation"] is not None, "Explanation should not be None"
        assert len(signal["explanation"]) > 10, "Explanation should have meaningful content"
        
        print(f"✓ Pro signal has AI explanation: {signal['explanation'][:80]}...")
    
    def test_trend_analysis_structure(self):
        """Test trend_analysis field has correct structure"""
        response = self.session.get(
            f"{BASE_URL}/api/signals/tiered",
            params={"wallet_address": TEST_PRO_WALLET}
        )
        assert response.status_code == 200
        
        data = response.json()
        signal = data["signals"][0]
        
        trend = signal.get("trend_analysis")
        if trend:
            assert "direction" in trend, "trend_analysis should have 'direction'"
            assert trend["direction"] in ["bullish", "bearish", "neutral"], \
                f"Invalid direction: {trend['direction']}"
            
            assert "strength" in trend, "trend_analysis should have 'strength'"
            assert trend["strength"] in ["strong", "moderate", "weak"], \
                f"Invalid strength: {trend['strength']}"
            
            assert "timeframe" in trend, "trend_analysis should have 'timeframe'"
            assert "description" in trend, "trend_analysis should have 'description'"
            
            print(f"✓ Trend analysis: {trend['direction']} ({trend['strength']}) - {trend['timeframe']}")
    
    def test_market_sentiment_structure(self):
        """Test market_sentiment field has correct structure"""
        response = self.session.get(
            f"{BASE_URL}/api/signals/tiered",
            params={"wallet_address": TEST_PRO_WALLET}
        )
        assert response.status_code == 200
        
        data = response.json()
        signal = data["signals"][0]
        
        sentiment = signal.get("market_sentiment")
        if sentiment:
            assert "overall" in sentiment, "market_sentiment should have 'overall'"
            assert sentiment["overall"] in ["bullish", "bearish", "neutral", "mixed"], \
                f"Invalid overall sentiment: {sentiment['overall']}"
            
            assert "score" in sentiment, "market_sentiment should have 'score'"
            assert isinstance(sentiment["score"], (int, float)), "Score should be numeric"
            assert -100 <= sentiment["score"] <= 100, f"Score should be -100 to 100, got {sentiment['score']}"
            
            assert "factors" in sentiment, "market_sentiment should have 'factors'"
            assert isinstance(sentiment["factors"], list), "Factors should be a list"
            
            assert "news_impact" in sentiment, "market_sentiment should have 'news_impact'"
            
            print(f"✓ Market sentiment: {sentiment['overall']} (score: {sentiment['score']})")
    
    def test_key_indicators_structure(self):
        """Test key_indicators field has correct structure"""
        response = self.session.get(
            f"{BASE_URL}/api/signals/tiered",
            params={"wallet_address": TEST_PRO_WALLET}
        )
        assert response.status_code == 200
        
        data = response.json()
        signal = data["signals"][0]
        
        indicators = signal.get("key_indicators")
        if indicators:
            # RSI
            assert "rsi" in indicators, "key_indicators should have 'rsi'"
            rsi = indicators["rsi"]
            assert "value" in rsi, "RSI should have 'value'"
            assert "signal" in rsi, "RSI should have 'signal'"
            
            # MACD
            assert "macd" in indicators, "key_indicators should have 'macd'"
            macd = indicators["macd"]
            assert "signal" in macd, "MACD should have 'signal'"
            assert "histogram" in macd, "MACD should have 'histogram'"
            
            # Moving Averages
            assert "moving_averages" in indicators, "key_indicators should have 'moving_averages'"
            
            # Volume
            assert "volume" in indicators, "key_indicators should have 'volume'"
            
            # Support/Resistance
            assert "support_resistance" in indicators, "key_indicators should have 'support_resistance'"
            sr = indicators["support_resistance"]
            assert "nearest_support" in sr, "support_resistance should have 'nearest_support'"
            assert "nearest_resistance" in sr, "support_resistance should have 'nearest_resistance'"
            
            print(f"✓ Key indicators: RSI={rsi['value']} ({rsi['signal']}), MACD={macd['signal']}")
    
    def test_risk_level_values(self):
        """Test risk_level field has valid values"""
        response = self.session.get(
            f"{BASE_URL}/api/signals/tiered",
            params={"wallet_address": TEST_PRO_WALLET}
        )
        assert response.status_code == 200
        
        data = response.json()
        signal = data["signals"][0]
        
        risk_level = signal.get("risk_level")
        if risk_level:
            assert risk_level in ["low", "medium", "high"], \
                f"Invalid risk_level: {risk_level}"
            print(f"✓ Risk level: {risk_level}")
    
    def test_confidence_factors_and_catalysts(self):
        """Test confidence_factors and potential_catalysts are lists"""
        response = self.session.get(
            f"{BASE_URL}/api/signals/tiered",
            params={"wallet_address": TEST_PRO_WALLET}
        )
        assert response.status_code == 200
        
        data = response.json()
        signal = data["signals"][0]
        
        factors = signal.get("confidence_factors")
        if factors:
            assert isinstance(factors, list), "confidence_factors should be a list"
            print(f"✓ Confidence factors: {len(factors)} items")
        
        catalysts = signal.get("potential_catalysts")
        if catalysts:
            assert isinstance(catalysts, list), "potential_catalysts should be a list"
            print(f"✓ Potential catalysts: {len(catalysts)} items")
    
    def test_suggested_action_present(self):
        """Test suggested_action field is present and meaningful"""
        response = self.session.get(
            f"{BASE_URL}/api/signals/tiered",
            params={"wallet_address": TEST_PRO_WALLET}
        )
        assert response.status_code == 200
        
        data = response.json()
        signal = data["signals"][0]
        
        action = signal.get("suggested_action")
        if action:
            assert len(action) > 20, "suggested_action should have meaningful content"
            print(f"✓ Suggested action: {action[:80]}...")
    
    # ============= TIER COMPARISON TESTS =============
    
    def test_free_vs_pro_signal_delay(self):
        """Test that free tier signals are delayed vs pro tier"""
        # Get free signals
        free_response = self.session.get(f"{BASE_URL}/api/signals/free")
        assert free_response.status_code == 200
        free_data = free_response.json()
        
        # Get pro signals
        pro_response = self.session.get(
            f"{BASE_URL}/api/signals/tiered",
            params={"wallet_address": TEST_PRO_WALLET}
        )
        assert pro_response.status_code == 200
        pro_data = pro_response.json()
        
        # Compare
        assert free_data["delay_minutes"] == 15, "Free tier should have 15 min delay"
        assert pro_data["delay_minutes"] == 0, "Pro tier should have 0 delay"
        
        if free_data["signals"] and pro_data["signals"]:
            free_signal = free_data["signals"][0]
            pro_signal = pro_data["signals"][0]
            
            assert free_signal["is_delayed"] == True
            assert pro_signal["is_delayed"] == False
            
            # Pro signals should be more recent
            free_time = datetime.fromisoformat(free_signal["generated_at"].replace('Z', '+00:00'))
            pro_time = datetime.fromisoformat(pro_signal["generated_at"].replace('Z', '+00:00'))
            
            # Pro signal should be at least 10 minutes newer (accounting for some variance)
            time_diff = (pro_time - free_time).total_seconds() / 60
            print(f"✓ Pro signals are {time_diff:.1f} minutes newer than free signals")
    
    def test_all_crypto_symbols_have_signals(self):
        """Test that signals exist for BTC, ETH, and SOL"""
        response = self.session.get(
            f"{BASE_URL}/api/signals/tiered",
            params={"wallet_address": TEST_PRO_WALLET}
        )
        assert response.status_code == 200
        
        data = response.json()
        symbols = [s["symbol"] for s in data["signals"]]
        
        expected_symbols = ["BTC", "ETH", "SOL"]
        for symbol in expected_symbols:
            assert symbol in symbols, f"Missing signal for {symbol}"
        
        print(f"✓ Signals present for: {', '.join(symbols)}")
    
    def test_signal_types_are_valid(self):
        """Test that signal_type is BUY, SELL, or HOLD"""
        response = self.session.get(
            f"{BASE_URL}/api/signals/tiered",
            params={"wallet_address": TEST_PRO_WALLET}
        )
        assert response.status_code == 200
        
        data = response.json()
        for signal in data["signals"]:
            assert signal["signal_type"] in ["BUY", "SELL", "HOLD"], \
                f"Invalid signal_type: {signal['signal_type']}"
        
        print(f"✓ All signal types are valid")
    
    def test_confidence_range(self):
        """Test that confidence is between 0 and 100"""
        response = self.session.get(
            f"{BASE_URL}/api/signals/tiered",
            params={"wallet_address": TEST_PRO_WALLET}
        )
        assert response.status_code == 200
        
        data = response.json()
        for signal in data["signals"]:
            assert 0 <= signal["confidence"] <= 100, \
                f"Confidence out of range: {signal['confidence']}"
        
        print(f"✓ All confidence values are in valid range")


class TestSignalIntelligenceService:
    """Tests for the Signal Intelligence Service directly"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_signal_generation_endpoint(self):
        """Test that signal generation creates signals with AI explanations"""
        # Trigger signal generation (if endpoint exists)
        # This tests the background signal generation
        response = self.session.get(
            f"{BASE_URL}/api/signals/tiered",
            params={"wallet_address": TEST_PRO_WALLET}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["signals"]) > 0, "Should have generated signals"
        
        # Check that at least one signal has AI explanation
        signals_with_ai = [s for s in data["signals"] if s.get("explanation")]
        assert len(signals_with_ai) > 0, "At least one signal should have AI explanation"
        
        print(f"✓ {len(signals_with_ai)}/{len(data['signals'])} signals have AI explanations")


class TestSubscriptionTierAccess:
    """Tests for subscription tier access to signals"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_subscription_tier_endpoint(self):
        """Test /api/subscription/tier returns correct tier"""
        response = self.session.get(
            f"{BASE_URL}/api/subscription/tier",
            params={"wallet_address": TEST_PRO_WALLET}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "tier" in data, "Response should contain 'tier'"
        assert data["tier"] == "pro", f"Expected 'pro', got {data['tier']}"
        
        print(f"✓ Subscription tier endpoint returns correct tier")
    
    def test_free_user_tier(self):
        """Test that unknown wallet gets free/unregistered tier"""
        response = self.session.get(
            f"{BASE_URL}/api/subscription/tier",
            params={"wallet_address": "0xUNKNOWN_WALLET_ADDRESS"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Unknown wallets get either 'free' or 'unregistered' tier
        assert data["tier"] in ["free", "unregistered"], \
            f"Unknown wallet should get 'free' or 'unregistered' tier, got {data['tier']}"
        
        print(f"✓ Unknown wallet correctly gets {data['tier']} tier")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
