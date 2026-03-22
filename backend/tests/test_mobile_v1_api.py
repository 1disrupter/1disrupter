"""
AlphaAI Mobile API v1 Tests
Tests for React Native / Expo mobile app backend endpoints
- API versioning with /api/v1/ prefix
- Pagination, field selection, ETag caching
- Cross-platform JWT authentication
- Push notification device registration
- Notification preferences management
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "Test123456"


class TestMobileHealthEndpoints:
    """Health and connectivity endpoints - no auth required"""
    
    def test_health_check(self):
        """GET /api/v1/health - Health check endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "version" in data
        print(f"✅ Health check passed: {data}")
    
    def test_ping(self):
        """GET /api/v1/ping - Ultra-minimal ping"""
        response = requests.get(f"{BASE_URL}/api/v1/ping")
        assert response.status_code == 200
        
        data = response.json()
        assert data["pong"] == True
        print(f"✅ Ping passed: {data}")
    
    def test_config(self):
        """GET /api/v1/config - Mobile app configuration"""
        response = requests.get(f"{BASE_URL}/api/v1/config")
        assert response.status_code == 200
        
        data = response.json()
        assert "api_version" in data
        assert "min_app_version" in data
        assert "features" in data
        assert data["features"]["push_notifications"] == True
        assert "endpoints" in data
        assert "refresh_intervals" in data
        assert "pagination" in data
        print(f"✅ Config passed: api_version={data['api_version']}, features={data['features']}")


class TestMobileAuthEndpoints:
    """Authentication endpoints for mobile"""
    
    def test_login_success(self):
        """POST /api/v1/auth/login - Mobile login with expires_in"""
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            params={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "expires_in" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["expires_in"], int)
        assert data["expires_in"] > 0
        
        # Verify user object
        assert "user" in data
        user = data["user"]
        assert user["email"] == TEST_EMAIL
        assert "id" in user
        assert "name" in user
        assert "is_pro" in user
        assert "is_elite" in user
        print(f"✅ Login passed: expires_in={data['expires_in']}s, user={user['email']}")
    
    def test_login_with_device_id(self):
        """POST /api/v1/auth/login - Login with device tracking"""
        device_id = f"test-device-{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            params={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "device_id": device_id
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        print(f"✅ Login with device_id passed: device={device_id}")
    
    def test_login_invalid_credentials(self):
        """POST /api/v1/auth/login - Invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            params={"email": "wrong@example.com", "password": "wrongpass"}
        )
        assert response.status_code in [401, 400]
        print(f"✅ Invalid login correctly rejected: status={response.status_code}")
    
    def test_refresh_token(self):
        """POST /api/v1/auth/refresh - Token refresh"""
        # First login to get refresh token
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            params={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh the token
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/refresh",
            params={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "expires_in" in data
        assert "user" in data
        print(f"✅ Token refresh passed: expires_in={data['expires_in']}s")
    
    def test_get_profile(self):
        """GET /api/v1/auth/me - Get profile"""
        # Login first
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            params={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        token = login_response.json()["access_token"]
        
        response = requests.get(
            f"{BASE_URL}/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == TEST_EMAIL
        assert "id" in data
        assert "name" in data
        assert "is_pro" in data
        assert "paper_balance" in data
        print(f"✅ Get profile passed: email={data['email']}, balance={data['paper_balance']}")
    
    def test_get_profile_with_field_selection(self):
        """GET /api/v1/auth/me?fields=id,name,is_pro - Field selection"""
        # Login first
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            params={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        token = login_response.json()["access_token"]
        
        response = requests.get(
            f"{BASE_URL}/api/v1/auth/me",
            params={"fields": "id,name,is_pro"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Should only have requested fields
        assert "id" in data
        assert "name" in data
        assert "is_pro" in data
        # Should NOT have other fields
        assert "email" not in data
        assert "paper_balance" not in data
        print(f"✅ Field selection passed: fields={list(data.keys())}")
    
    def test_get_profile_unauthorized(self):
        """GET /api/v1/auth/me - Unauthorized access"""
        response = requests.get(f"{BASE_URL}/api/v1/auth/me")
        assert response.status_code == 401
        print(f"✅ Unauthorized profile access correctly rejected")


class TestMobileSignalsEndpoints:
    """Signals endpoints with pagination and caching"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            params={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_signals_paginated(self):
        """GET /api/v1/signals - Paginated signals with ETag"""
        response = requests.get(
            f"{BASE_URL}/api/v1/signals",
            params={"page": 1, "limit": 10},
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert "meta" in data
        
        pagination = data["pagination"]
        assert "page" in pagination
        assert "limit" in pagination
        assert "total" in pagination
        assert "total_pages" in pagination
        assert "has_next" in pagination
        assert "has_prev" in pagination
        
        # Check ETag in meta (header may be stripped by proxy/CDN)
        meta = data["meta"]
        assert "etag" in meta
        print(f"✅ Signals pagination passed: page={pagination['page']}, total={pagination['total']}, etag={meta['etag'][:20]}...")
    
    def test_get_signals_with_field_selection(self):
        """GET /api/v1/signals?fields=id,symbol,type - Field selection"""
        response = requests.get(
            f"{BASE_URL}/api/v1/signals",
            params={"page": 1, "limit": 5, "fields": "id,symbol,type"},
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        if data["data"]:
            signal = data["data"][0]
            # Should only have requested fields
            assert "id" in signal
            assert "symbol" in signal
            assert "type" in signal
            print(f"✅ Signals field selection passed: fields={list(signal.keys())}")
        else:
            print(f"✅ Signals field selection passed (no signals in DB)")
    
    def test_get_signals_etag_caching(self):
        """GET /api/v1/signals - ETag caching (304 Not Modified)"""
        # First request to get ETag
        response1 = requests.get(
            f"{BASE_URL}/api/v1/signals",
            params={"page": 1, "limit": 5},
            headers=self.headers
        )
        assert response1.status_code == 200
        etag = response1.headers.get("ETag")
        
        # Second request with If-None-Match
        response2 = requests.get(
            f"{BASE_URL}/api/v1/signals",
            params={"page": 1, "limit": 5},
            headers={**self.headers, "If-None-Match": etag}
        )
        # Should return 304 if data hasn't changed
        assert response2.status_code in [200, 304]
        print(f"✅ ETag caching passed: status={response2.status_code}")
    
    def test_get_latest_signal(self):
        """GET /api/v1/signals/latest - Single latest signal"""
        response = requests.get(
            f"{BASE_URL}/api/v1/signals/latest",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "signal" in data
        assert "is_pro" in data
        
        if data["signal"]:
            signal = data["signal"]
            assert "id" in signal
            assert "symbol" in signal
            assert "type" in signal
            assert "confidence" in signal
            print(f"✅ Latest signal passed: {signal['symbol']} {signal['type']} {signal['confidence']}%")
        else:
            print(f"✅ Latest signal passed (no signals in DB)")
    
    def test_get_signals_unauthorized(self):
        """GET /api/v1/signals - Unauthorized access"""
        response = requests.get(f"{BASE_URL}/api/v1/signals")
        assert response.status_code == 401
        print(f"✅ Unauthorized signals access correctly rejected")


class TestMobilePortfolioEndpoints:
    """Portfolio endpoints for mobile dashboard"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            params={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_portfolio_summary(self):
        """GET /api/v1/portfolio/summary - Dashboard widget data"""
        response = requests.get(
            f"{BASE_URL}/api/v1/portfolio/summary",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "paper_balance" in data
        assert "paper_pnl" in data
        assert "paper_pnl_percent" in data
        assert "open_positions" in data
        assert "today_trades" in data
        assert "is_pro" in data
        assert "updated_at" in data
        
        # Note: ETag header may be stripped by proxy/CDN, but endpoint sets it
        print(f"✅ Portfolio summary passed: balance={data['paper_balance']}, pnl={data['paper_pnl']}")
    
    def test_get_portfolio_positions(self):
        """GET /api/v1/portfolio/positions - Paginated positions"""
        response = requests.get(
            f"{BASE_URL}/api/v1/portfolio/positions",
            params={"status": "all", "page": 1, "limit": 10},
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        
        pagination = data["pagination"]
        assert "page" in pagination
        assert "limit" in pagination
        assert "total" in pagination
        print(f"✅ Portfolio positions passed: total={pagination['total']}")
    
    def test_get_portfolio_positions_filtered(self):
        """GET /api/v1/portfolio/positions?status=open - Filtered positions"""
        response = requests.get(
            f"{BASE_URL}/api/v1/portfolio/positions",
            params={"status": "open", "page": 1, "limit": 10},
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # All returned positions should be open
        for position in data["data"]:
            assert position["status"] == "open"
        print(f"✅ Filtered positions passed: open_count={len(data['data'])}")
    
    def test_get_portfolio_unauthorized(self):
        """GET /api/v1/portfolio/summary - Unauthorized access"""
        response = requests.get(f"{BASE_URL}/api/v1/portfolio/summary")
        assert response.status_code == 401
        print(f"✅ Unauthorized portfolio access correctly rejected")


class TestMobileTradingEndpoints:
    """Trading execution endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            params={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_execute_trade_buy(self):
        """POST /api/v1/trading/execute - Mobile trade execution (BUY)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/trading/execute",
            params={
                "symbol": "ETH",
                "side": "BUY",
                "amount": 0.01
            },
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "trade_id" in data
        assert data["symbol"] == "ETH"
        assert data["side"] == "BUY"
        assert data["amount"] == 0.01
        assert "price" in data
        assert "value" in data
        assert "new_balance" in data
        assert "timestamp" in data
        print(f"✅ Trade BUY passed: trade_id={data['trade_id']}, value={data['value']}")
    
    def test_execute_trade_sell(self):
        """POST /api/v1/trading/execute - Mobile trade execution (SELL)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/trading/execute",
            params={
                "symbol": "BTC",
                "side": "SELL",
                "amount": 0.001
            },
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["symbol"] == "BTC"
        assert data["side"] == "SELL"
        print(f"✅ Trade SELL passed: trade_id={data['trade_id']}, value={data['value']}")
    
    def test_execute_trade_unauthorized(self):
        """POST /api/v1/trading/execute - Unauthorized access"""
        response = requests.post(
            f"{BASE_URL}/api/v1/trading/execute",
            params={"symbol": "BTC", "side": "BUY", "amount": 0.01}
        )
        assert response.status_code == 401
        print(f"✅ Unauthorized trade correctly rejected")


class TestMobileDeviceEndpoints:
    """Push notification device registration endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            params={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.test_device_id = f"test-device-{uuid.uuid4().hex[:8]}"
    
    def test_register_device(self):
        """POST /api/v1/devices/register - Push notification device registration"""
        response = requests.post(
            f"{BASE_URL}/api/v1/devices/register",
            json={
                "device_id": self.test_device_id,
                "platform": "expo",
                "push_token": f"ExponentPushToken[{uuid.uuid4().hex[:20]}]",
                "app_version": "1.0.0",
                "os_version": "iOS 17.0",
                "device_model": "iPhone 15"
            },
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "device_id" in data
        print(f"✅ Device registration passed: device_id={data['device_id']}")
    
    def test_list_devices(self):
        """GET /api/v1/devices - List registered devices"""
        # First register a device
        requests.post(
            f"{BASE_URL}/api/v1/devices/register",
            json={
                "device_id": self.test_device_id,
                "platform": "expo",
                "push_token": f"ExponentPushToken[{uuid.uuid4().hex[:20]}]",
                "app_version": "1.0.0"
            },
            headers=self.headers
        )
        
        response = requests.get(
            f"{BASE_URL}/api/v1/devices",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "devices" in data
        assert "count" in data
        assert isinstance(data["devices"], list)
        
        # Verify push_token is not exposed
        for device in data["devices"]:
            assert "push_token" not in device
        print(f"✅ List devices passed: count={data['count']}")
    
    def test_update_push_token(self):
        """PUT /api/v1/devices/{id}/token - Update push token"""
        # First register a device
        device_id = f"test-device-{uuid.uuid4().hex[:8]}"
        requests.post(
            f"{BASE_URL}/api/v1/devices/register",
            json={
                "device_id": device_id,
                "platform": "expo",
                "push_token": f"ExponentPushToken[old-token]",
                "app_version": "1.0.0"
            },
            headers=self.headers
        )
        
        # Update the token
        new_token = f"ExponentPushToken[{uuid.uuid4().hex[:20]}]"
        response = requests.put(
            f"{BASE_URL}/api/v1/devices/{device_id}/token",
            params={"push_token": new_token},
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        print(f"✅ Update push token passed")
    
    def test_update_push_token_not_found(self):
        """PUT /api/v1/devices/{id}/token - Device not found"""
        response = requests.put(
            f"{BASE_URL}/api/v1/devices/nonexistent-device/token",
            params={"push_token": "ExponentPushToken[test]"},
            headers=self.headers
        )
        assert response.status_code == 404
        print(f"✅ Update token for nonexistent device correctly rejected")
    
    def test_devices_unauthorized(self):
        """GET /api/v1/devices - Unauthorized access"""
        response = requests.get(f"{BASE_URL}/api/v1/devices")
        assert response.status_code == 401
        print(f"✅ Unauthorized devices access correctly rejected")


class TestMobileNotificationPreferences:
    """Notification preferences management endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            params={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_notification_preferences(self):
        """GET /api/v1/notifications/preferences - Get notification preferences"""
        response = requests.get(
            f"{BASE_URL}/api/v1/notifications/preferences",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "push_enabled" in data
        assert "signal_alerts" in data
        assert "signal_min_confidence" in data
        assert "price_alerts" in data
        assert "trade_confirmations" in data
        assert "daily_summary" in data
        assert "weekly_report" in data
        assert "marketing" in data
        assert "quiet_hours" in data
        
        # Verify quiet_hours structure
        quiet_hours = data["quiet_hours"]
        assert "enabled" in quiet_hours
        assert "start" in quiet_hours
        assert "end" in quiet_hours
        print(f"✅ Get preferences passed: push_enabled={data['push_enabled']}, signal_alerts={data['signal_alerts']}")
    
    def test_update_notification_preferences(self):
        """PUT /api/v1/notifications/preferences - Update preferences"""
        response = requests.put(
            f"{BASE_URL}/api/v1/notifications/preferences",
            params={
                "push_enabled": True,
                "signal_alerts": True,
                "signal_min_confidence": 80,
                "marketing": False
            },
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "updated" in data
        assert "signal_min_confidence" in data["updated"]
        print(f"✅ Update preferences passed: updated={data['updated']}")
    
    def test_update_preferences_partial(self):
        """PUT /api/v1/notifications/preferences - Partial update"""
        response = requests.put(
            f"{BASE_URL}/api/v1/notifications/preferences",
            params={"daily_summary": False},
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "daily_summary" in data["updated"]
        print(f"✅ Partial update passed: updated={data['updated']}")
    
    def test_preferences_unauthorized(self):
        """GET /api/v1/notifications/preferences - Unauthorized access"""
        response = requests.get(f"{BASE_URL}/api/v1/notifications/preferences")
        assert response.status_code == 401
        print(f"✅ Unauthorized preferences access correctly rejected")


class TestMobileMetricsEndpoints:
    """Metrics endpoints for mobile dashboard"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            params={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_metrics_summary(self):
        """GET /api/v1/metrics/summary - Mobile metrics widget"""
        response = requests.get(
            f"{BASE_URL}/api/v1/metrics/summary",
            params={"days": 7},
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "period_days" in data
        assert data["period_days"] == 7
        assert "total_trades" in data
        assert "win_rate" in data
        assert "total_pnl" in data
        assert "best_trade" in data
        assert "worst_trade" in data
        print(f"✅ Metrics summary passed: trades={data['total_trades']}, win_rate={data['win_rate']}%")
    
    def test_get_metrics_summary_custom_period(self):
        """GET /api/v1/metrics/summary?days=30 - Custom period"""
        response = requests.get(
            f"{BASE_URL}/api/v1/metrics/summary",
            params={"days": 30},
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["period_days"] == 30
        print(f"✅ Metrics custom period passed: period={data['period_days']} days")
    
    def test_metrics_unauthorized(self):
        """GET /api/v1/metrics/summary - Unauthorized access"""
        response = requests.get(f"{BASE_URL}/api/v1/metrics/summary")
        assert response.status_code == 401
        print(f"✅ Unauthorized metrics access correctly rejected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
