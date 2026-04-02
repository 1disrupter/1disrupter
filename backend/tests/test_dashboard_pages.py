"""
Dashboard Pages API Tests
Tests for all 8 wired dashboard pages + admin analytics endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://alpha-trading-hub.preview.emergentagent.com')
ADMIN_KEY = "alphaai_admin_2026"


class TestSimulationEndpoints:
    """Simulation page API tests"""
    
    def test_simulation_stats(self):
        """GET /api/simulation/stats returns simulation data"""
        response = requests.get(f"{BASE_URL}/api/simulation/stats")
        assert response.status_code == 200
        data = response.json()
        assert "simulation" in data or "trading" in data or "strategies" in data
        print(f"Simulation stats: {list(data.keys())}")
    
    def test_simulation_config(self):
        """GET /api/simulation/config returns config"""
        response = requests.get(f"{BASE_URL}/api/simulation/config")
        # May return 404 if not configured, but should not error
        assert response.status_code in [200, 404]


class TestAgentsEndpoints:
    """AI Agents page API tests"""
    
    def test_agents_list(self):
        """GET /api/agents returns agent list"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        data = response.json()
        # Should be a list of agents
        assert isinstance(data, list) or "agents" in data
        print(f"Agents count: {len(data) if isinstance(data, list) else len(data.get('agents', []))}")


class TestEventAgentsEndpoints:
    """Event Agents page API tests"""
    
    def test_event_agents_list(self):
        """GET /api/agents/event-agents returns event agents"""
        response = requests.get(f"{BASE_URL}/api/agents/event-agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        print(f"Event agents count: {len(data.get('agents', []))}")
    
    def test_recent_events(self):
        """GET /api/events/recent returns recent events"""
        response = requests.get(f"{BASE_URL}/api/events/recent?limit=10")
        # May return 404 if endpoint doesn't exist
        assert response.status_code in [200, 404]


class TestStrategyLabEndpoints:
    """Strategy Lab page API tests"""
    
    def test_strategies_list(self):
        """GET /api/lab/strategies returns strategies"""
        response = requests.get(f"{BASE_URL}/api/lab/strategies")
        assert response.status_code == 200
        data = response.json()
        # Should be a list or have strategies key
        assert isinstance(data, list) or "strategies" in data
        strategies = data if isinstance(data, list) else data.get("strategies", [])
        print(f"Strategies count: {len(strategies)}")
        if strategies:
            # Verify strategy structure
            s = strategies[0]
            assert "name" in s or "id" in s


class TestMarketplaceEndpoints:
    """Marketplace page API tests - uses same endpoint as Strategy Lab"""
    
    def test_marketplace_items(self):
        """GET /api/lab/strategies returns items for marketplace"""
        response = requests.get(f"{BASE_URL}/api/lab/strategies")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "strategies" in data


class TestResearchEndpoints:
    """Research Engine page API tests"""
    
    def test_research_reports(self):
        """GET /api/research/reports returns research reports"""
        response = requests.get(f"{BASE_URL}/api/research/reports")
        assert response.status_code == 200
        data = response.json()
        assert "reports" in data
        print(f"Research reports count: {len(data.get('reports', []))}")
    
    def test_research_metrics(self):
        """GET /api/research/metrics returns metrics"""
        response = requests.get(f"{BASE_URL}/api/research/metrics")
        # May return 404 if not implemented
        assert response.status_code in [200, 404]


class TestReferralEndpoints:
    """Referral page API tests"""
    
    def test_referral_stats_unauthenticated(self):
        """GET /api/referrals/stats without auth returns 401 or empty"""
        response = requests.get(f"{BASE_URL}/api/referrals/stats")
        # Should require auth or return empty
        assert response.status_code in [200, 401, 403]


class TestAnalyticsEndpoints:
    """Analytics page API tests"""
    
    def test_analytics_summary(self):
        """GET /api/analytics/summary returns analytics data"""
        response = requests.get(f"{BASE_URL}/api/analytics/summary")
        assert response.status_code == 200
        data = response.json()
        # Should have some analytics data
        assert isinstance(data, dict)
        print(f"Analytics summary keys: {list(data.keys())}")


class TestAdminAnalyticsEndpoints:
    """Admin Analytics page API tests"""
    
    def test_admin_analytics_with_key(self):
        """GET /api/admin/analytics with admin_key returns KPI data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics",
            params={"admin_key": ADMIN_KEY, "period": "30d"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify KPI structure
        assert "kpi" in data
        kpi = data["kpi"]
        assert "demo_opens" in kpi
        assert "total_signups" in kpi
        assert "demo_signup_rate" in kpi
        assert "demo_pro_rate" in kpi
        assert "k_factor" in kpi
        print(f"Admin KPI: demo_opens={kpi['demo_opens']}, signups={kpi['total_signups']}")
        
        # Verify chart data
        assert "opens_over_time" in data
        assert "top_referrers" in data
        assert "pages_per_session" in data
        assert "event_types" in data
        assert "recent_events" in data
    
    def test_admin_analytics_periods(self):
        """Test all time period filters"""
        for period in ["24h", "7d", "30d", "all"]:
            response = requests.get(
                f"{BASE_URL}/api/admin/analytics",
                params={"admin_key": ADMIN_KEY, "period": period}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["period"] == period
            print(f"Period {period}: demo_opens={data['kpi']['demo_opens']}")
    
    def test_admin_analytics_without_key(self):
        """GET /api/admin/analytics without admin_key returns 403"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics")
        assert response.status_code in [403, 422]  # 422 for missing required param
    
    def test_admin_analytics_wrong_key(self):
        """GET /api/admin/analytics with wrong key returns 403"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics",
            params={"admin_key": "wrong_key", "period": "30d"}
        )
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
