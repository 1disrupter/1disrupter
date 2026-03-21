"""
Backend API tests for AlphaAI Dashboard Redesign
Tests: /api/live-prices, /api/market/live-prices, /api/fund/stats
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://trading-signals-lab-1.preview.emergentagent.com').rstrip('/')

class TestDashboardAPIs:
    """Dashboard-related API endpoint tests"""
    
    def test_live_prices_endpoint(self):
        """Test /api/live-prices endpoint returns crypto prices"""
        response = requests.get(f"{BASE_URL}/api/live-prices", timeout=10)
        
        # Should return 200
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Should have prices array
        assert "prices" in data, "Response should contain 'prices' key"
        assert isinstance(data["prices"], list), "'prices' should be a list"
        assert len(data["prices"]) > 0, "'prices' should not be empty"
        
        # Check first price has expected fields
        price_item = data["prices"][0]
        assert "symbol" in price_item, "Price item should have 'symbol'"
        assert "price" in price_item, "Price item should have 'price'"
        assert "change_24h" in price_item, "Price item should have 'change_24h'"
        
        print(f"✅ /api/live-prices returned {len(data['prices'])} prices")
    
    def test_market_live_prices_endpoint(self):
        """Test /api/market/live-prices endpoint returns crypto prices"""
        response = requests.get(f"{BASE_URL}/api/market/live-prices", timeout=10)
        
        # Should return 200
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Should have prices array
        assert "prices" in data, "Response should contain 'prices' key"
        assert isinstance(data["prices"], list), "'prices' should be a list"
        
        print(f"✅ /api/market/live-prices returned {len(data['prices'])} prices")
    
    def test_fund_stats_endpoint(self):
        """Test /api/fund/stats endpoint returns fund statistics"""
        response = requests.get(f"{BASE_URL}/api/fund/stats", timeout=10)
        
        # Should return 200
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Should have expected fund stat fields
        assert "nav" in data, "Response should contain 'nav'"
        assert "total_aum" in data, "Response should contain 'total_aum'"
        assert "sharpe_ratio" in data, "Response should contain 'sharpe_ratio'"
        assert "monthly_return" in data, "Response should contain 'monthly_return'"
        
        print(f"✅ /api/fund/stats returned NAV: ${data['nav']:.2f}, AUM: ${data['total_aum']:.2f}")
    
    def test_api_root_health(self):
        """Test API root endpoint for health check"""
        response = requests.get(f"{BASE_URL}/api/", timeout=10)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ API root health check passed")


class TestSimulationAPIs:
    """Simulation-related API endpoint tests"""
    
    def test_simulation_config(self):
        """Test /api/simulation/config endpoint"""
        response = requests.get(f"{BASE_URL}/api/simulation/config", timeout=10)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "is_running" in data or "mode" in data, "Should have simulation config fields"
        print("✅ /api/simulation/config endpoint working")
    
    def test_simulation_stats(self):
        """Test /api/simulation/stats endpoint"""
        response = requests.get(f"{BASE_URL}/api/simulation/stats", timeout=10)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "simulation" in data or "trading" in data, "Should have stats fields"
        print("✅ /api/simulation/stats endpoint working")


class TestStrategyLabAPIs:
    """Strategy Lab API endpoint tests"""
    
    def test_lab_strategies(self):
        """Test /api/lab/strategies endpoint"""
        response = requests.get(f"{BASE_URL}/api/lab/strategies", timeout=10)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Should return a list of strategies"
        print(f"✅ /api/lab/strategies returned {len(data)} strategies")
    
    def test_lab_rankings(self):
        """Test /api/lab/rankings endpoint"""
        response = requests.get(f"{BASE_URL}/api/lab/rankings", timeout=10)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Should return a list of rankings"
        print(f"✅ /api/lab/rankings returned {len(data)} ranked strategies")


class TestAgentsAPIs:
    """AI Agents API endpoint tests"""
    
    def test_agents_list(self):
        """Test /api/agents endpoint"""
        response = requests.get(f"{BASE_URL}/api/agents", timeout=10)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Should return a list of agents"
        print(f"✅ /api/agents returned {len(data)} agents")
    
    def test_trades_list(self):
        """Test /api/trades endpoint"""
        response = requests.get(f"{BASE_URL}/api/trades?limit=10", timeout=10)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Should return a list of trades"
        print(f"✅ /api/trades returned {len(data)} trades")
    
    def test_risk_portfolio_status(self):
        """Test /api/risk/portfolio-status endpoint"""
        response = requests.get(f"{BASE_URL}/api/risk/portfolio-status", timeout=10)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "current_drawdown" in data or "risk_level" in data, "Should have risk status fields"
        print("✅ /api/risk/portfolio-status endpoint working")


class TestInvestorAPIs:
    """Investor API endpoint tests"""
    
    def test_investor_registration(self):
        """Test /api/investors/register endpoint"""
        test_wallet = "0xTEST_dashboard_" + str(os.urandom(4).hex())
        
        response = requests.post(
            f"{BASE_URL}/api/investors/register",
            json={"wallet_address": test_wallet},
            timeout=10
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "wallet_address" in data, "Should return investor with wallet_address"
        print(f"✅ Investor registration works for wallet: {test_wallet[:20]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
