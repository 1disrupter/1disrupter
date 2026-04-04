"""
Strategy Leaderboard API Tests
Tests for GET /api/marketplace/strategies/leaderboard endpoint
- Default sorting by total_return desc
- Sorting by sharpe_ratio, win_rate, max_drawdown
- Ascending and descending order
- Response structure validation
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestStrategyLeaderboard:
    """Tests for /api/marketplace/strategies/leaderboard endpoint"""
    
    def test_leaderboard_returns_200(self):
        """Leaderboard endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Leaderboard endpoint returns 200")
    
    def test_leaderboard_returns_strategies_array(self):
        """Leaderboard returns strategies array with total count"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard")
        data = response.json()
        assert "strategies" in data, "Response missing 'strategies' key"
        assert "total" in data, "Response missing 'total' key"
        assert isinstance(data["strategies"], list), "strategies should be a list"
        assert isinstance(data["total"], int), "total should be an integer"
        print(f"✓ Leaderboard returns {data['total']} strategies")
    
    def test_leaderboard_has_public_strategies(self):
        """Leaderboard returns at least 7 public strategies"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard")
        data = response.json()
        # Per context: 3 featured + 4 pre-existing = 7 public strategies
        assert data["total"] >= 7, f"Expected at least 7 strategies, got {data['total']}"
        print(f"✓ Leaderboard has {data['total']} public strategies (expected >= 7)")
    
    def test_strategies_have_perf_data(self):
        """Each strategy has _perf object with performance metrics"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard")
        data = response.json()
        
        for s in data["strategies"]:
            assert "_perf" in s, f"Strategy {s.get('name')} missing _perf"
            perf = s["_perf"]
            # _perf can be empty dict if no performance uploaded
            if perf:
                # Check expected fields exist when perf data is present
                expected_fields = ["sharpe_ratio", "win_rate", "max_drawdown", "total_return"]
                for field in expected_fields:
                    assert field in perf, f"Strategy {s.get('name')} _perf missing {field}"
        print("✓ All strategies have _perf data structure")
    
    def test_strategies_have_required_fields(self):
        """Each strategy has required display fields"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard")
        data = response.json()
        
        required_fields = ["id", "name", "creator_name", "category", "status", "is_public"]
        for s in data["strategies"]:
            for field in required_fields:
                assert field in s, f"Strategy missing required field: {field}"
            # All should be published and public
            assert s["status"] == "published", f"Strategy {s['name']} not published"
            assert s["is_public"] == True, f"Strategy {s['name']} not public"
        print("✓ All strategies have required fields and are published/public")
    
    def test_default_sort_by_total_return_desc(self):
        """Default sort is by total_return descending"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard")
        data = response.json()
        strategies = data["strategies"]
        
        if len(strategies) >= 2:
            returns = [s.get("_perf", {}).get("total_return") or 0 for s in strategies]
            # Check descending order
            for i in range(len(returns) - 1):
                assert returns[i] >= returns[i+1], f"Not sorted by total_return desc: {returns[i]} < {returns[i+1]}"
        print("✓ Default sort is by total_return descending")
    
    def test_sort_by_sharpe_ratio_asc(self):
        """Sort by sharpe_ratio ascending works"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard?sort_by=sharpe_ratio&order=asc")
        assert response.status_code == 200
        data = response.json()
        strategies = data["strategies"]
        
        if len(strategies) >= 2:
            sharpes = [s.get("_perf", {}).get("sharpe_ratio") or 0 for s in strategies]
            for i in range(len(sharpes) - 1):
                assert sharpes[i] <= sharpes[i+1], f"Not sorted by sharpe_ratio asc: {sharpes[i]} > {sharpes[i+1]}"
        print("✓ Sort by sharpe_ratio ascending works")
    
    def test_sort_by_sharpe_ratio_desc(self):
        """Sort by sharpe_ratio descending works"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard?sort_by=sharpe_ratio&order=desc")
        assert response.status_code == 200
        data = response.json()
        strategies = data["strategies"]
        
        if len(strategies) >= 2:
            sharpes = [s.get("_perf", {}).get("sharpe_ratio") or 0 for s in strategies]
            for i in range(len(sharpes) - 1):
                assert sharpes[i] >= sharpes[i+1], f"Not sorted by sharpe_ratio desc: {sharpes[i]} < {sharpes[i+1]}"
        print("✓ Sort by sharpe_ratio descending works")
    
    def test_sort_by_win_rate_desc(self):
        """Sort by win_rate descending works"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard?sort_by=win_rate&order=desc")
        assert response.status_code == 200
        data = response.json()
        strategies = data["strategies"]
        
        if len(strategies) >= 2:
            win_rates = [s.get("_perf", {}).get("win_rate") or 0 for s in strategies]
            for i in range(len(win_rates) - 1):
                assert win_rates[i] >= win_rates[i+1], f"Not sorted by win_rate desc: {win_rates[i]} < {win_rates[i+1]}"
        print("✓ Sort by win_rate descending works")
    
    def test_sort_by_win_rate_asc(self):
        """Sort by win_rate ascending works"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard?sort_by=win_rate&order=asc")
        assert response.status_code == 200
        data = response.json()
        strategies = data["strategies"]
        
        if len(strategies) >= 2:
            win_rates = [s.get("_perf", {}).get("win_rate") or 0 for s in strategies]
            for i in range(len(win_rates) - 1):
                assert win_rates[i] <= win_rates[i+1], f"Not sorted by win_rate asc: {win_rates[i]} > {win_rates[i+1]}"
        print("✓ Sort by win_rate ascending works")
    
    def test_sort_by_max_drawdown_desc(self):
        """Sort by max_drawdown descending works"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard?sort_by=max_drawdown&order=desc")
        assert response.status_code == 200
        data = response.json()
        strategies = data["strategies"]
        
        if len(strategies) >= 2:
            drawdowns = [s.get("_perf", {}).get("max_drawdown") or 0 for s in strategies]
            for i in range(len(drawdowns) - 1):
                assert drawdowns[i] >= drawdowns[i+1], f"Not sorted by max_drawdown desc: {drawdowns[i]} < {drawdowns[i+1]}"
        print("✓ Sort by max_drawdown descending works")
    
    def test_sort_by_max_drawdown_asc(self):
        """Sort by max_drawdown ascending works"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard?sort_by=max_drawdown&order=asc")
        assert response.status_code == 200
        data = response.json()
        strategies = data["strategies"]
        
        if len(strategies) >= 2:
            drawdowns = [s.get("_perf", {}).get("max_drawdown") or 0 for s in strategies]
            for i in range(len(drawdowns) - 1):
                assert drawdowns[i] <= drawdowns[i+1], f"Not sorted by max_drawdown asc: {drawdowns[i]} > {drawdowns[i+1]}"
        print("✓ Sort by max_drawdown ascending works")
    
    def test_invalid_sort_field_defaults_to_total_return(self):
        """Invalid sort_by field defaults to total_return"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard?sort_by=invalid_field")
        assert response.status_code == 200
        data = response.json()
        strategies = data["strategies"]
        
        # Should still be sorted by total_return desc (default)
        if len(strategies) >= 2:
            returns = [s.get("_perf", {}).get("total_return") or 0 for s in strategies]
            for i in range(len(returns) - 1):
                assert returns[i] >= returns[i+1], "Invalid sort_by should default to total_return desc"
        print("✓ Invalid sort_by defaults to total_return")
    
    def test_featured_strategies_in_leaderboard(self):
        """Featured strategies (Alpha Momentum BTC, ETH Reversal Sniper, SOL Breakout Pulse) are in leaderboard"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard")
        data = response.json()
        
        strategy_names = [s["name"] for s in data["strategies"]]
        featured_names = ["Alpha Momentum BTC", "ETH Reversal Sniper", "SOL Breakout Pulse"]
        
        for name in featured_names:
            assert name in strategy_names, f"Featured strategy '{name}' not in leaderboard"
        print("✓ All 3 featured strategies are in leaderboard")
    
    def test_pre_existing_strategies_in_leaderboard(self):
        """Pre-existing strategies (BTC Momentum Alpha, SOL Trend Follower, Multi-Asset Arbitrage, ETH Scalping Bot) are in leaderboard"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard")
        data = response.json()
        
        strategy_names = [s["name"] for s in data["strategies"]]
        pre_existing = ["BTC Momentum Alpha", "SOL Trend Follower", "Multi-Asset Arbitrage", "ETH Scalping Bot"]
        
        for name in pre_existing:
            assert name in strategy_names, f"Pre-existing strategy '{name}' not in leaderboard"
        print("✓ All 4 pre-existing strategies are in leaderboard")


class TestStrategyDetailFromLeaderboard:
    """Test that strategy detail pages work for leaderboard strategies"""
    
    def test_strategy_detail_accessible(self):
        """Strategy detail endpoint works for leaderboard strategies"""
        # Get first strategy from leaderboard
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard")
        data = response.json()
        
        if data["strategies"]:
            strategy_id = data["strategies"][0]["id"]
            detail_response = requests.get(f"{BASE_URL}/api/marketplace/strategies/{strategy_id}")
            assert detail_response.status_code == 200, f"Strategy detail returned {detail_response.status_code}"
            
            detail = detail_response.json()
            assert "strategy" in detail, "Detail missing 'strategy' key"
            assert "performance" in detail, "Detail missing 'performance' key"
            print(f"✓ Strategy detail accessible for {data['strategies'][0]['name']}")


class TestNoRegression:
    """Regression tests to ensure existing functionality still works"""
    
    def test_health_endpoint(self):
        """Health endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✓ Health endpoint works")
    
    def test_featured_endpoint(self):
        """Featured strategies endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/marketplace/featured")
        assert response.status_code == 200
        data = response.json()
        assert "strategies" in data
        assert len(data["strategies"]) == 3, f"Expected 3 featured, got {len(data['strategies'])}"
        print("✓ Featured endpoint returns 3 strategies")
    
    def test_marketplace_strategies_list(self):
        """Marketplace strategies list still works"""
        response = requests.get(f"{BASE_URL}/api/marketplace/strategies")
        assert response.status_code == 200
        data = response.json()
        assert "strategies" in data
        assert "total" in data
        print(f"✓ Marketplace list returns {data['total']} strategies")
    
    def test_login_works(self):
        """Login still works with test credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo_test2@my-alpha-ai.com",
            "password": "NewPass1234!"
        })
        assert response.status_code == 200, f"Login failed: {response.status_code}"
        data = response.json()
        assert "access_token" in data, "Login response missing access_token"
        print("✓ Login works with test credentials")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
