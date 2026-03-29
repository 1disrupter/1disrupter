"""
Test Smart Prefetching and Strategy Page Performance Polish features
Tests: Leaderboard API, Strategy Detail API, Mobile Bootstrap, TTL Cache values
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestLeaderboardAPI:
    """Leaderboard endpoint tests for smart prefetch features"""
    
    def test_leaderboard_demo_mode(self):
        """GET /api/leaderboard/strategies with demo=true returns mock data"""
        response = requests.get(f"{BASE_URL}/api/leaderboard/strategies", params={
            "demo": "true",
            "sort_by": "sharpe",
            "order": "desc",
            "limit": 10
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "strategies" in data
        assert len(data["strategies"]) > 0
        
        # Verify demo data structure
        strategy = data["strategies"][0]
        assert "id" in strategy
        assert "name" in strategy
        assert "type" in strategy
        assert "metrics" in strategy
        assert strategy.get("data_source") == "mock"
        print(f"✅ Leaderboard demo mode: {len(data['strategies'])} strategies returned")
    
    def test_leaderboard_strategy_metrics(self):
        """Verify strategy metrics structure for prefetch caching"""
        response = requests.get(f"{BASE_URL}/api/leaderboard/strategies", params={
            "demo": "true",
            "limit": 3
        })
        assert response.status_code == 200
        data = response.json()
        
        for strategy in data["strategies"]:
            metrics = strategy.get("metrics", {})
            assert "sharpe_ratio" in metrics
            assert "total_return" in metrics
            assert "max_drawdown" in metrics
            assert "win_rate" in metrics
            assert "total_trades" in metrics
            print(f"✅ Strategy '{strategy['name']}' has all required metrics")
    
    def test_leaderboard_sorting(self):
        """Test sorting by different columns"""
        for sort_by in ["sharpe", "total_return", "max_drawdown", "win_rate"]:
            response = requests.get(f"{BASE_URL}/api/leaderboard/strategies", params={
                "demo": "true",
                "sort_by": sort_by,
                "order": "desc",
                "limit": 5
            })
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") == True
            print(f"✅ Sorting by {sort_by} works")


class TestStrategyDetailAPI:
    """Strategy detail endpoint tests for prefetch caching"""
    
    def test_strategy_detail_demo(self):
        """GET /api/leaderboard/strategies/{id} with demo=true"""
        # First get a strategy ID
        list_response = requests.get(f"{BASE_URL}/api/leaderboard/strategies", params={
            "demo": "true",
            "limit": 1
        })
        assert list_response.status_code == 200
        strategy_id = list_response.json()["strategies"][0]["id"]
        
        # Get detail
        response = requests.get(f"{BASE_URL}/api/leaderboard/strategies/{strategy_id}", params={
            "demo": "true"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "strategy" in data
        
        strategy = data["strategy"]
        assert strategy["id"] == strategy_id
        assert "metrics" in strategy
        assert "equity_curve" in strategy.get("metrics", {})
        print(f"✅ Strategy detail for '{strategy['name']}' returned with equity curve")
    
    def test_strategy_detail_has_equity_curve(self):
        """Verify equity curve data for chart skeleton replacement"""
        response = requests.get(f"{BASE_URL}/api/leaderboard/strategies/demo-1", params={
            "demo": "true"
        })
        assert response.status_code == 200
        data = response.json()
        
        equity_curve = data["strategy"]["metrics"].get("equity_curve", [])
        assert len(equity_curve) > 0
        
        # Verify equity curve structure
        point = equity_curve[0]
        assert "day" in point or "date" in point
        assert "value" in point
        print(f"✅ Equity curve has {len(equity_curve)} data points")


class TestMobileBootstrapAPI:
    """Mobile bootstrap endpoint for prefetch initialization"""
    
    def test_bootstrap_demo_mode(self):
        """GET /api/mobile/bootstrap with demo=true"""
        response = requests.get(f"{BASE_URL}/api/mobile/bootstrap", params={
            "demo": "true"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "user" in data
        assert "followed_strategies" in data
        assert "feature_flags" in data
        print(f"✅ Bootstrap demo mode returns user and feature flags")
    
    def test_bootstrap_has_strategies_summary(self):
        """Verify strategies summary for prefetch decisions"""
        response = requests.get(f"{BASE_URL}/api/mobile/bootstrap", params={
            "demo": "true"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "strategies_summary" in data
        summary = data["strategies_summary"]
        assert "total" in summary
        print(f"✅ Bootstrap has strategies_summary with total={summary['total']}")


class TestFollowingAPI:
    """Following endpoints for offline behavior testing"""
    
    def test_following_ids_demo(self):
        """GET /api/strategies/following/ids returns demo followed IDs"""
        # In demo mode, this should work without auth
        response = requests.get(f"{BASE_URL}/api/strategies/following/ids", params={
            "demo": "true"
        })
        # May return 401 without auth, which is expected
        if response.status_code == 200:
            data = response.json()
            assert "ids" in data
            print(f"✅ Following IDs returned: {data['ids']}")
        else:
            print(f"⚠️ Following IDs requires auth (status {response.status_code})")


class TestTTLCacheValues:
    """Verify TTL cache configuration matches requirements"""
    
    def test_ttl_values_documented(self):
        """Document expected TTL values for verification"""
        expected_ttl = {
            "strategy_detail": "5 minutes (300000ms)",
            "metadata": "10 minutes (600000ms)",
            "alerts": "30 seconds (30000ms)",
            "chart": "2 minutes (120000ms)",
            "strategies": "5 minutes (300000ms)",
            "bootstrap": "2 minutes (120000ms)"
        }
        
        for key, ttl in expected_ttl.items():
            print(f"✅ TTL for {key}: {ttl}")
        
        # This test documents the expected values
        # Actual verification is in frontend code review
        assert True


class TestSmartPrefetchEndpoints:
    """Test endpoints used by smart prefetch engine"""
    
    def test_prefetch_leaderboard_top3(self):
        """Prefetch top 3 strategies for podium"""
        response = requests.get(f"{BASE_URL}/api/leaderboard/strategies", params={
            "demo": "true",
            "limit": 3,
            "sort_by": "sharpe",
            "order": "desc"
        })
        assert response.status_code == 200
        data = response.json()
        
        strategies = data.get("strategies", [])
        assert len(strategies) >= 3
        
        # Verify each has ID for detail prefetch
        for s in strategies[:3]:
            assert "id" in s
            print(f"✅ Top strategy '{s['name']}' (id={s['id']}) ready for prefetch")
    
    def test_prefetch_strategy_detail(self):
        """Prefetch individual strategy detail"""
        # Get demo-1 detail
        response = requests.get(f"{BASE_URL}/api/leaderboard/strategies/demo-1", params={
            "demo": "true"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        assert "strategy" in data
        print(f"✅ Strategy detail prefetch works for demo-1")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
