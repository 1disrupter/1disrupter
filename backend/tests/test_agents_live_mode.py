"""
Test Agents Live Mode System - Iteration 72
Tests for:
- GET /api/agents — returns 4 real agents with metrics
- GET /api/agents/{id}/signals — returns real signals from agents
- PUT /api/agents/{id}/config — updates agent config
- GET /api/signals/live — returns real live signals
- GET /api/portfolio/performance — returns equity curve data
- GET /api/portfolio/trades — returns trade history
- GET /api/portfolio/summary — returns portfolio summary
- GET /api/demo-mode/status — returns demo mode status
- POST /api/admin/demo-mode — toggle demo mode
- Auth and Marketplace still work
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "mar-brick@hotmail.com"
ADMIN_PASSWORD = "Martin2026!"
ADMIN_KEY = "alphaai_admin_2026"


class TestDemoModeStatus:
    """Test demo mode status endpoint"""
    
    def test_get_demo_mode_status(self):
        """GET /api/demo-mode/status returns demo_mode boolean"""
        response = requests.get(f"{BASE_URL}/api/demo-mode/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "demo_mode" in data, "Response should contain demo_mode field"
        assert isinstance(data["demo_mode"], bool), "demo_mode should be boolean"
        print(f"✓ Demo mode status: {data['demo_mode']}")


class TestDemoModeToggle:
    """Test demo mode toggle functionality"""
    
    def test_toggle_demo_mode_on(self):
        """POST /api/admin/demo-mode with enabled:true turns demo ON"""
        response = requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": True}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("demo_mode") == True or data.get("enabled") == True, "Demo mode should be enabled"
        print("✓ Demo mode toggled ON")
    
    def test_toggle_demo_mode_off(self):
        """POST /api/admin/demo-mode with enabled:false turns demo OFF"""
        response = requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": False}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("demo_mode") == False or data.get("enabled") == False, "Demo mode should be disabled"
        print("✓ Demo mode toggled OFF")
    
    def test_toggle_demo_mode_invalid_key(self):
        """POST /api/admin/demo-mode with invalid key returns 403"""
        response = requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key=wrong_key",
            json={"enabled": True}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Invalid admin key rejected with 403")


class TestAgentsAPI:
    """Test agents API endpoints"""
    
    def test_list_agents_returns_4_agents(self):
        """GET /api/agents returns 4 real agents with metrics"""
        # First ensure demo mode is OFF
        requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": False}
        )
        time.sleep(0.5)  # Allow cache to clear
        
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "agents" in data, "Response should contain agents array"
        agents = data["agents"]
        assert len(agents) == 4, f"Expected 4 agents, got {len(agents)}"
        
        # Verify agent structure
        expected_ids = ["momentum-scanner", "sentiment-analyzer", "whale-tracker", "volatility-engine"]
        agent_ids = [a["id"] for a in agents]
        for eid in expected_ids:
            assert eid in agent_ids, f"Missing agent: {eid}"
        
        # Verify each agent has required fields
        for agent in agents:
            assert "id" in agent, "Agent should have id"
            assert "name" in agent, "Agent should have name"
            assert "status" in agent, "Agent should have status"
            assert "assets" in agent, "Agent should have assets"
            assert "total_signals" in agent or "signals" in agent, "Agent should have signal count"
            print(f"  ✓ Agent: {agent['name']} - {agent.get('total_signals', 0)} total signals")
        
        print(f"✓ GET /api/agents returned {len(agents)} agents")
    
    def test_list_agents_demo_mode(self):
        """GET /api/agents returns demo data when demo mode ON"""
        # Turn demo mode ON
        requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": True}
        )
        time.sleep(0.5)
        
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("demo_mode") == True, "Should indicate demo_mode: true"
        assert len(data["agents"]) == 4, "Should return 4 demo agents"
        print("✓ GET /api/agents returns demo data when demo mode ON")
        
        # Turn demo mode back OFF
        requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": False}
        )


class TestAgentSignals:
    """Test agent signals endpoints"""
    
    def test_get_momentum_scanner_signals(self):
        """GET /api/agents/momentum-scanner/signals returns real signals"""
        # Ensure demo mode OFF
        requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": False}
        )
        time.sleep(0.5)
        
        response = requests.get(f"{BASE_URL}/api/agents/momentum-scanner/signals?limit=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "signals" in data, "Response should contain signals array"
        assert "agent_id" in data, "Response should contain agent_id"
        assert data["agent_id"] == "momentum-scanner"
        
        signals = data["signals"]
        print(f"✓ Momentum Scanner has {len(signals)} signals")
        
        # Verify signal structure if signals exist
        if signals:
            sig = signals[0]
            assert "symbol" in sig, "Signal should have symbol"
            assert "signal_type" in sig, "Signal should have signal_type"
            assert "confidence" in sig, "Signal should have confidence"
            print(f"  Sample signal: {sig['symbol']} {sig['signal_type']} @ {sig.get('confidence', 0)}% confidence")
    
    def test_get_sentiment_analyzer_signals(self):
        """GET /api/agents/sentiment-analyzer/signals returns real signals"""
        response = requests.get(f"{BASE_URL}/api/agents/sentiment-analyzer/signals?limit=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "signals" in data
        assert data["agent_id"] == "sentiment-analyzer"
        print(f"✓ Sentiment Analyzer has {len(data['signals'])} signals")


class TestAgentConfig:
    """Test agent configuration endpoint"""
    
    def test_update_agent_config(self):
        """PUT /api/agents/momentum-scanner/config updates config successfully"""
        response = requests.put(
            f"{BASE_URL}/api/agents/momentum-scanner/config",
            json={"risk_level": "aggressive"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "message" in data or "agent_id" in data, "Response should confirm update"
        print("✓ Agent config updated successfully")
        
        # Reset to moderate
        requests.put(
            f"{BASE_URL}/api/agents/momentum-scanner/config",
            json={"risk_level": "moderate"}
        )
    
    def test_update_agent_config_no_fields(self):
        """PUT /api/agents/momentum-scanner/config with empty body returns 400"""
        response = requests.put(
            f"{BASE_URL}/api/agents/momentum-scanner/config",
            json={}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Empty config update rejected with 400")


class TestLiveSignals:
    """Test live signals endpoint"""
    
    def test_get_live_signals(self):
        """GET /api/signals/live returns real live signals"""
        # Ensure demo mode OFF
        requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": False}
        )
        time.sleep(0.5)
        
        response = requests.get(f"{BASE_URL}/api/signals/live?limit=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "signals" in data, "Response should contain signals array"
        assert "demo_mode" in data, "Response should contain demo_mode flag"
        assert data["demo_mode"] == False, "demo_mode should be false"
        
        print(f"✓ GET /api/signals/live returned {len(data['signals'])} signals (demo_mode: {data['demo_mode']})")
    
    def test_get_live_signals_demo_mode(self):
        """GET /api/signals/live returns demo signals when demo mode ON"""
        # Turn demo mode ON
        requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": True}
        )
        time.sleep(0.5)
        
        response = requests.get(f"{BASE_URL}/api/signals/live?limit=5")
        assert response.status_code == 200
        data = response.json()
        
        assert data["demo_mode"] == True, "demo_mode should be true"
        assert len(data["signals"]) > 0, "Should return demo signals"
        
        # Check demo signal has is_demo flag
        if data["signals"]:
            assert data["signals"][0].get("is_demo") == True, "Demo signals should have is_demo: true"
        
        print("✓ GET /api/signals/live returns demo signals when demo mode ON")
        
        # Turn demo mode back OFF
        requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": False}
        )


class TestPortfolioEndpoints:
    """Test portfolio endpoints"""
    
    def test_portfolio_performance(self):
        """GET /api/portfolio/performance returns equity curve data"""
        response = requests.get(f"{BASE_URL}/api/portfolio/performance?user_id=test&days=7")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "equity_curve" in data, "Response should contain equity_curve"
        assert "demo_mode" in data, "Response should contain demo_mode flag"
        
        print(f"✓ GET /api/portfolio/performance returned {len(data.get('equity_curve', []))} data points")
    
    def test_portfolio_trades(self):
        """GET /api/portfolio/trades returns trade history"""
        response = requests.get(f"{BASE_URL}/api/portfolio/trades?user_id=test&limit=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "trades" in data, "Response should contain trades array"
        assert "demo_mode" in data, "Response should contain demo_mode flag"
        
        print(f"✓ GET /api/portfolio/trades returned {len(data.get('trades', []))} trades")
    
    def test_portfolio_summary(self):
        """GET /api/portfolio/summary returns portfolio summary"""
        response = requests.get(f"{BASE_URL}/api/portfolio/summary?user_id=test")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "total_pnl" in data, "Response should contain total_pnl"
        assert "demo_mode" in data, "Response should contain demo_mode flag"
        
        print(f"✓ GET /api/portfolio/summary returned total_pnl: {data.get('total_pnl', 0)}")


class TestAuthStillWorks:
    """Verify auth endpoints still work"""
    
    def test_login_returns_access_token(self):
        """POST /api/auth/login returns access_token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "access_token" in data, "Response should contain access_token"
        assert len(data["access_token"]) > 0, "access_token should not be empty"
        
        print("✓ POST /api/auth/login returns access_token")


class TestMarketplaceStillWorks:
    """Verify marketplace endpoints still work"""
    
    def test_marketplace_leaderboard(self):
        """GET /api/marketplace/strategies/leaderboard returns strategies"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Should return strategies array or similar structure
        assert isinstance(data, (list, dict)), "Response should be list or dict"
        
        print("✓ GET /api/marketplace/strategies/leaderboard works")


class TestFullDemoModeFlow:
    """Test complete demo mode toggle flow"""
    
    def test_full_demo_mode_flow(self):
        """Full flow: toggle ON → verify agents return demo → toggle OFF → verify real"""
        # Step 1: Toggle demo ON
        resp1 = requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": True}
        )
        assert resp1.status_code == 200
        time.sleep(0.5)
        
        # Step 2: Verify agents return demo data
        resp2 = requests.get(f"{BASE_URL}/api/agents")
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2.get("demo_mode") == True, "Agents should return demo_mode: true"
        print("  ✓ Demo mode ON: agents return demo data")
        
        # Step 3: Toggle demo OFF
        resp3 = requests.post(
            f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
            json={"enabled": False}
        )
        assert resp3.status_code == 200
        time.sleep(0.5)
        
        # Step 4: Verify agents return real data
        resp4 = requests.get(f"{BASE_URL}/api/agents")
        assert resp4.status_code == 200
        data4 = resp4.json()
        assert data4.get("demo_mode") == False, "Agents should return demo_mode: false"
        print("  ✓ Demo mode OFF: agents return real data")
        
        print("✓ Full demo mode toggle flow works correctly")


class TestHealthCheck:
    """Basic health check"""
    
    def test_health_endpoint(self):
        """GET /api/health returns 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Health check passed")


# Cleanup: Ensure demo mode is OFF after all tests
@pytest.fixture(scope="session", autouse=True)
def cleanup_demo_mode():
    yield
    # After all tests, ensure demo mode is OFF
    requests.post(
        f"{BASE_URL}/api/admin/demo-mode?admin_key={ADMIN_KEY}",
        json={"enabled": False}
    )
    print("\n✓ Cleanup: Demo mode set to OFF")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
