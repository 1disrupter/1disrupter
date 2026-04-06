"""
Marketplace Featured Strategies Tests
Tests for featured strategies, strategy detail, and copy functionality
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://routing-split.preview.emergentagent.com')

# Test credentials
PRO_USER_EMAIL = "demo_test2@my-alpha-ai.com"
PRO_USER_PASSWORD = "NewPass1234!"

# Known strategy IDs from seed
STRATEGY_IDS = {
    "alpha_momentum_btc": "9ff5661a-e5a1-483b-bcf1-e3484ea72b7e",
    "eth_reversal_sniper": "ce84d244-1659-444d-b41e-f030cfc5f5c4",
    "sol_breakout_pulse": "6af36c43-4600-4356-8595-da62a369cc1a"
}


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Get authentication token for pro user"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": PRO_USER_EMAIL,
        "password": PRO_USER_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


class TestHealthCheck:
    """Health check endpoint"""
    
    def test_health_endpoint(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("PASS: Health endpoint returns healthy status")


class TestFeaturedStrategies:
    """Tests for GET /api/marketplace/featured endpoint"""
    
    def test_featured_returns_200(self, api_client):
        """Featured endpoint returns 200 OK"""
        response = api_client.get(f"{BASE_URL}/api/marketplace/featured")
        assert response.status_code == 200
        print("PASS: Featured endpoint returns 200")
    
    def test_featured_returns_3_strategies(self, api_client):
        """Featured endpoint returns exactly 3 strategies"""
        response = api_client.get(f"{BASE_URL}/api/marketplace/featured")
        data = response.json()
        assert "strategies" in data
        assert len(data["strategies"]) == 3
        print(f"PASS: Featured returns 3 strategies")
    
    def test_featured_strategies_have_perf_data(self, api_client):
        """Each featured strategy has _perf data with required metrics"""
        response = api_client.get(f"{BASE_URL}/api/marketplace/featured")
        data = response.json()
        
        for s in data["strategies"]:
            assert "_perf" in s, f"Strategy {s['name']} missing _perf"
            perf = s["_perf"]
            assert "sharpe_ratio" in perf, f"Strategy {s['name']} missing sharpe_ratio"
            assert "win_rate" in perf, f"Strategy {s['name']} missing win_rate"
            assert "max_drawdown" in perf, f"Strategy {s['name']} missing max_drawdown"
            assert "total_return" in perf, f"Strategy {s['name']} missing total_return"
            print(f"PASS: {s['name']} has complete _perf data")
    
    def test_featured_strategies_have_risk_labels(self, api_client):
        """Each featured strategy has a risk_label"""
        response = api_client.get(f"{BASE_URL}/api/marketplace/featured")
        data = response.json()
        
        expected_labels = {"Medium", "Medium-High", "High"}
        for s in data["strategies"]:
            assert "risk_label" in s, f"Strategy {s['name']} missing risk_label"
            assert s["risk_label"] in expected_labels, f"Invalid risk_label: {s['risk_label']}"
            print(f"PASS: {s['name']} has risk_label: {s['risk_label']}")
    
    def test_featured_strategies_are_published(self, api_client):
        """All featured strategies have status=published and is_public=true"""
        response = api_client.get(f"{BASE_URL}/api/marketplace/featured")
        data = response.json()
        
        for s in data["strategies"]:
            assert s["status"] == "published", f"Strategy {s['name']} not published"
            assert s["is_public"] == True, f"Strategy {s['name']} not public"
            assert s["featured"] == True, f"Strategy {s['name']} not featured"
            print(f"PASS: {s['name']} is published, public, and featured")


class TestMarketplaceStrategies:
    """Tests for GET /api/marketplace/strategies endpoint"""
    
    def test_strategies_list_returns_200(self, api_client):
        """Strategies list endpoint returns 200"""
        response = api_client.get(f"{BASE_URL}/api/marketplace/strategies")
        assert response.status_code == 200
        print("PASS: Strategies list returns 200")
    
    def test_strategies_list_includes_featured(self, api_client):
        """Strategies list includes the 3 featured strategies"""
        response = api_client.get(f"{BASE_URL}/api/marketplace/strategies")
        data = response.json()
        
        strategy_ids = [s["id"] for s in data["strategies"]]
        for name, sid in STRATEGY_IDS.items():
            assert sid in strategy_ids, f"Featured strategy {name} not in list"
            print(f"PASS: Featured strategy {name} found in list")


class TestStrategyDetail:
    """Tests for GET /api/marketplace/strategies/{id} endpoint"""
    
    def test_strategy_detail_returns_200(self, api_client):
        """Strategy detail endpoint returns 200 for valid ID"""
        sid = STRATEGY_IDS["alpha_momentum_btc"]
        response = api_client.get(f"{BASE_URL}/api/marketplace/strategies/{sid}")
        assert response.status_code == 200
        print("PASS: Strategy detail returns 200")
    
    def test_strategy_detail_has_full_data(self, api_client):
        """Strategy detail includes strategy, performance, signals, reviews"""
        sid = STRATEGY_IDS["alpha_momentum_btc"]
        response = api_client.get(f"{BASE_URL}/api/marketplace/strategies/{sid}")
        data = response.json()
        
        assert "strategy" in data
        assert "performance" in data
        assert "signals" in data
        assert "reviews" in data
        print("PASS: Strategy detail has all required fields")
    
    def test_strategy_detail_performance_data(self, api_client):
        """Strategy detail performance has required metrics"""
        sid = STRATEGY_IDS["alpha_momentum_btc"]
        response = api_client.get(f"{BASE_URL}/api/marketplace/strategies/{sid}")
        data = response.json()
        
        perf = data["performance"]
        assert perf is not None
        assert perf["sharpe_ratio"] == 2.14
        assert perf["win_rate"] == 62.8
        assert perf["max_drawdown"] == -11.3
        assert perf["total_return"] == 47.2
        print("PASS: Strategy detail has correct performance metrics")
    
    def test_strategy_detail_has_risk_label(self, api_client):
        """Strategy detail includes risk_label"""
        sid = STRATEGY_IDS["alpha_momentum_btc"]
        response = api_client.get(f"{BASE_URL}/api/marketplace/strategies/{sid}")
        data = response.json()
        
        assert data["strategy"]["risk_label"] == "Medium"
        print("PASS: Strategy detail has risk_label")
    
    def test_strategy_detail_404_for_invalid_id(self, api_client):
        """Strategy detail returns 404 for invalid ID"""
        response = api_client.get(f"{BASE_URL}/api/marketplace/strategies/invalid-id-12345")
        assert response.status_code == 404
        print("PASS: Strategy detail returns 404 for invalid ID")


class TestCopyStrategy:
    """Tests for POST /api/marketplace/strategies/{id}/copy endpoint"""
    
    def test_copy_requires_auth(self, api_client):
        """Copy endpoint requires authentication"""
        sid = STRATEGY_IDS["eth_reversal_sniper"]
        response = api_client.post(f"{BASE_URL}/api/marketplace/strategies/{sid}/copy")
        assert response.status_code in [401, 403]
        print("PASS: Copy endpoint requires authentication")
    
    def test_copy_strategy_success(self, api_client, auth_token):
        """Copy strategy creates a copy in user's collection"""
        sid = STRATEGY_IDS["sol_breakout_pulse"]
        response = api_client.post(
            f"{BASE_URL}/api/marketplace/strategies/{sid}/copy",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "Strategy copied" in data["message"]
        assert "strategy" in data
        
        copied = data["strategy"]
        assert "(Copy)" in copied["name"]
        assert copied["status"] == "draft"
        assert copied["is_public"] == False
        assert copied["copied_from"] == sid
        print(f"PASS: Strategy copied successfully: {copied['name']}")
    
    def test_copy_strategy_404_for_invalid_id(self, api_client, auth_token):
        """Copy returns 404 for invalid strategy ID"""
        response = api_client.post(
            f"{BASE_URL}/api/marketplace/strategies/invalid-id-12345/copy",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404
        print("PASS: Copy returns 404 for invalid ID")


class TestRegressionChecks:
    """Regression tests for existing functionality"""
    
    def test_live_prices_endpoint(self, api_client):
        """Live prices endpoint still works"""
        response = api_client.get(f"{BASE_URL}/api/market/live-prices")
        assert response.status_code == 200
        print("PASS: Live prices endpoint works")
    
    def test_login_works(self, api_client):
        """Login endpoint works with test credentials"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": PRO_USER_EMAIL,
            "password": PRO_USER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print("PASS: Login works with test credentials")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
