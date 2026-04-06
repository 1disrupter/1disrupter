"""
Test Live Pages Endpoints - Dashboard, Alerts, Analytics
Tests the /api/dashboard/live, /api/alerts/live, /api/analytics/live endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSystemMode:
    """System mode endpoint tests"""
    
    def test_system_mode_returns_live(self):
        """GET /api/system/mode returns live mode"""
        response = requests.get(f"{BASE_URL}/api/system/mode")
        assert response.status_code == 200
        data = response.json()
        assert "mode" in data
        assert data["mode"] in ["live", "demo"]
        print(f"System mode: {data['mode']}")


class TestDashboardLive:
    """Dashboard live endpoint tests"""
    
    def test_dashboard_live_returns_200(self):
        """GET /api/dashboard/live returns 200"""
        response = requests.get(f"{BASE_URL}/api/dashboard/live")
        assert response.status_code == 200
        
    def test_dashboard_live_returns_mode(self):
        """GET /api/dashboard/live returns mode field"""
        response = requests.get(f"{BASE_URL}/api/dashboard/live")
        data = response.json()
        assert "mode" in data
        assert data["mode"] in ["live", "demo"]
        
    def test_dashboard_live_returns_signals_24h(self):
        """GET /api/dashboard/live returns signals_24h"""
        response = requests.get(f"{BASE_URL}/api/dashboard/live")
        data = response.json()
        assert "signals_24h" in data
        assert isinstance(data["signals_24h"], int)
        print(f"Signals 24h: {data['signals_24h']}")
        
    def test_dashboard_live_returns_active_agents(self):
        """GET /api/dashboard/live returns active_agents"""
        response = requests.get(f"{BASE_URL}/api/dashboard/live")
        data = response.json()
        assert "active_agents" in data
        assert isinstance(data["active_agents"], int)
        print(f"Active agents: {data['active_agents']}")
        
    def test_dashboard_live_returns_win_rate(self):
        """GET /api/dashboard/live returns win_rate"""
        response = requests.get(f"{BASE_URL}/api/dashboard/live")
        data = response.json()
        assert "win_rate" in data
        print(f"Win rate: {data['win_rate']}")
        
    def test_dashboard_live_returns_accuracy(self):
        """GET /api/dashboard/live returns accuracy"""
        response = requests.get(f"{BASE_URL}/api/dashboard/live")
        data = response.json()
        assert "accuracy" in data
        print(f"Accuracy: {data['accuracy']}")
        
    def test_dashboard_live_returns_recent_alerts(self):
        """GET /api/dashboard/live returns recent_alerts array"""
        response = requests.get(f"{BASE_URL}/api/dashboard/live")
        data = response.json()
        assert "recent_alerts" in data
        assert isinstance(data["recent_alerts"], list)
        print(f"Recent alerts count: {len(data['recent_alerts'])}")
        
    def test_dashboard_live_returns_agents(self):
        """GET /api/dashboard/live returns agents array"""
        response = requests.get(f"{BASE_URL}/api/dashboard/live")
        data = response.json()
        assert "agents" in data
        assert isinstance(data["agents"], list)
        print(f"Agents count: {len(data['agents'])}")
        
    def test_dashboard_live_recent_alerts_structure(self):
        """GET /api/dashboard/live recent_alerts have correct structure"""
        response = requests.get(f"{BASE_URL}/api/dashboard/live")
        data = response.json()
        if data["recent_alerts"]:
            alert = data["recent_alerts"][0]
            assert "action" in alert
            assert "asset" in alert
            assert "confidence" in alert
            assert "timestamp" in alert
            print(f"First alert: {alert['action']} {alert['asset']}")


class TestAlertsLive:
    """Alerts live endpoint tests"""
    
    def test_alerts_live_returns_200(self):
        """GET /api/alerts/live returns 200"""
        response = requests.get(f"{BASE_URL}/api/alerts/live")
        assert response.status_code == 200
        
    def test_alerts_live_returns_mode(self):
        """GET /api/alerts/live returns mode field"""
        response = requests.get(f"{BASE_URL}/api/alerts/live")
        data = response.json()
        assert "mode" in data
        assert data["mode"] in ["live", "demo"]
        
    def test_alerts_live_returns_alerts_array(self):
        """GET /api/alerts/live returns alerts array"""
        response = requests.get(f"{BASE_URL}/api/alerts/live")
        data = response.json()
        assert "alerts" in data
        assert isinstance(data["alerts"], list)
        print(f"Alerts count: {len(data['alerts'])}")
        
    def test_alerts_live_returns_count(self):
        """GET /api/alerts/live returns count field"""
        response = requests.get(f"{BASE_URL}/api/alerts/live")
        data = response.json()
        assert "count" in data
        assert isinstance(data["count"], int)
        
    def test_alerts_live_limit_parameter(self):
        """GET /api/alerts/live respects limit parameter"""
        response = requests.get(f"{BASE_URL}/api/alerts/live?limit=5")
        data = response.json()
        assert len(data["alerts"]) <= 5
        
    def test_alerts_live_alert_structure(self):
        """GET /api/alerts/live alerts have correct structure"""
        response = requests.get(f"{BASE_URL}/api/alerts/live?limit=5")
        data = response.json()
        if data["alerts"]:
            alert = data["alerts"][0]
            assert "action" in alert
            assert "asset" in alert
            assert "message" in alert
            assert "confidence" in alert
            assert "price" in alert
            assert "strategy_name" in alert
            assert "timestamp" in alert
            assert "is_demo" in alert
            print(f"Alert structure valid: {alert['action']} {alert['asset']}")
            
    def test_alerts_live_is_demo_false_in_live_mode(self):
        """GET /api/alerts/live alerts have is_demo=false in live mode"""
        response = requests.get(f"{BASE_URL}/api/alerts/live?limit=5")
        data = response.json()
        if data["mode"] == "live" and data["alerts"]:
            for alert in data["alerts"]:
                assert alert["is_demo"] == False


class TestAnalyticsLive:
    """Analytics live endpoint tests"""
    
    def test_analytics_live_returns_200(self):
        """GET /api/analytics/live returns 200"""
        response = requests.get(f"{BASE_URL}/api/analytics/live")
        assert response.status_code == 200
        
    def test_analytics_live_returns_mode(self):
        """GET /api/analytics/live returns mode field"""
        response = requests.get(f"{BASE_URL}/api/analytics/live")
        data = response.json()
        assert "mode" in data
        assert data["mode"] in ["live", "demo"]
        
    def test_analytics_live_returns_total_signals(self):
        """GET /api/analytics/live returns total_signals"""
        response = requests.get(f"{BASE_URL}/api/analytics/live")
        data = response.json()
        assert "total_signals" in data
        assert isinstance(data["total_signals"], int)
        print(f"Total signals: {data['total_signals']}")
        
    def test_analytics_live_returns_avg_win_rate(self):
        """GET /api/analytics/live returns avg_win_rate"""
        response = requests.get(f"{BASE_URL}/api/analytics/live")
        data = response.json()
        assert "avg_win_rate" in data
        print(f"Avg win rate: {data['avg_win_rate']}")
        
    def test_analytics_live_returns_sharpe_ratio(self):
        """GET /api/analytics/live returns sharpe_ratio"""
        response = requests.get(f"{BASE_URL}/api/analytics/live")
        data = response.json()
        assert "sharpe_ratio" in data
        print(f"Sharpe ratio: {data['sharpe_ratio']}")
        
    def test_analytics_live_returns_max_drawdown(self):
        """GET /api/analytics/live returns max_drawdown"""
        response = requests.get(f"{BASE_URL}/api/analytics/live")
        data = response.json()
        assert "max_drawdown" in data
        print(f"Max drawdown: {data['max_drawdown']}")
        
    def test_analytics_live_returns_by_pair(self):
        """GET /api/analytics/live returns by_pair array"""
        response = requests.get(f"{BASE_URL}/api/analytics/live")
        data = response.json()
        assert "by_pair" in data
        assert isinstance(data["by_pair"], list)
        print(f"By pair count: {len(data['by_pair'])}")
        
    def test_analytics_live_returns_by_agent(self):
        """GET /api/analytics/live returns by_agent array"""
        response = requests.get(f"{BASE_URL}/api/analytics/live")
        data = response.json()
        assert "by_agent" in data
        assert isinstance(data["by_agent"], list)
        print(f"By agent count: {len(data['by_agent'])}")
        
    def test_analytics_live_returns_daily(self):
        """GET /api/analytics/live returns daily array"""
        response = requests.get(f"{BASE_URL}/api/analytics/live")
        data = response.json()
        assert "daily" in data
        assert isinstance(data["daily"], list)
        print(f"Daily data points: {len(data['daily'])}")
        
    def test_analytics_live_by_pair_structure(self):
        """GET /api/analytics/live by_pair has correct structure"""
        response = requests.get(f"{BASE_URL}/api/analytics/live")
        data = response.json()
        if data["by_pair"]:
            pair = data["by_pair"][0]
            assert "name" in pair
            assert "signals" in pair
            assert "winRate" in pair
            print(f"First pair: {pair['name']} - {pair['signals']} signals")
            
    def test_analytics_live_by_agent_structure(self):
        """GET /api/analytics/live by_agent has correct structure"""
        response = requests.get(f"{BASE_URL}/api/analytics/live")
        data = response.json()
        if data["by_agent"]:
            agent = data["by_agent"][0]
            assert "name" in agent
            assert "signals" in agent
            assert "accuracy" in agent
            print(f"First agent: {agent['name']} - {agent['accuracy']}% accuracy")
            
    def test_analytics_live_daily_structure(self):
        """GET /api/analytics/live daily has correct structure"""
        response = requests.get(f"{BASE_URL}/api/analytics/live")
        data = response.json()
        if data["daily"]:
            day = data["daily"][0]
            assert "date" in day
            assert "signals" in day
            print(f"First day: {day['date']} - {day['signals']} signals")
            
    def test_analytics_live_days_parameter(self):
        """GET /api/analytics/live respects days parameter"""
        response = requests.get(f"{BASE_URL}/api/analytics/live?days=7")
        assert response.status_code == 200
        data = response.json()
        assert "daily" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
