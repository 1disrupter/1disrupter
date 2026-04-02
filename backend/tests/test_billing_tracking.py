"""
Billing Portal & Tracking Middleware API Tests
Tests for:
- GET /api/billing/overview - returns active_subscriptions, monthly_cost, total_spent, total_payments
- GET /api/billing/subscriptions - returns active and canceled subscriptions with strategy details
- GET /api/billing/payments - returns payment transaction history
- POST /api/admin/track - records page_view and api_call events (no auth required)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
PRO_USER_EMAIL = "demo_test2@my-alpha-ai.com"
PRO_USER_PASSWORD = "NewPass1234!"
FREE_USER_EMAIL = "test_free_user_iter29@my-alpha-ai.com"
FREE_USER_PASSWORD = "TestPass123!"


@pytest.fixture(scope="module")
def pro_user_token():
    """Get auth token for pro user with subscriptions"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": PRO_USER_EMAIL,
        "password": PRO_USER_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Pro user login failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def free_user_token():
    """Get auth token for free user without subscriptions"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": FREE_USER_EMAIL,
        "password": FREE_USER_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Free user login failed: {response.status_code} - {response.text}")


class TestBillingOverview:
    """Tests for GET /api/billing/overview endpoint"""

    def test_billing_overview_returns_correct_fields(self, pro_user_token):
        """Overview returns active_subscriptions, monthly_cost, total_spent, total_payments"""
        response = requests.get(
            f"{BASE_URL}/api/billing/overview",
            headers={"Authorization": f"Bearer {pro_user_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify all required fields exist
        assert "active_subscriptions" in data, "Missing active_subscriptions field"
        assert "monthly_cost" in data, "Missing monthly_cost field"
        assert "total_spent" in data, "Missing total_spent field"
        assert "total_payments" in data, "Missing total_payments field"
        assert "currency" in data, "Missing currency field"
        
        # Verify data types
        assert isinstance(data["active_subscriptions"], int), "active_subscriptions should be int"
        assert isinstance(data["monthly_cost"], (int, float)), "monthly_cost should be numeric"
        assert isinstance(data["total_spent"], (int, float)), "total_spent should be numeric"
        assert isinstance(data["total_payments"], int), "total_payments should be int"
        
        print(f"Overview: {data['active_subscriptions']} active subs, ${data['monthly_cost']}/mo, ${data['total_spent']} total spent, {data['total_payments']} payments")

    def test_billing_overview_requires_auth(self):
        """Overview endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/billing/overview")
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"

    def test_billing_overview_free_user(self, free_user_token):
        """Free user can access overview (may have 0 subscriptions)"""
        response = requests.get(
            f"{BASE_URL}/api/billing/overview",
            headers={"Authorization": f"Bearer {free_user_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "active_subscriptions" in data
        print(f"Free user overview: {data['active_subscriptions']} active subs")


class TestBillingSubscriptions:
    """Tests for GET /api/billing/subscriptions endpoint"""

    def test_billing_subscriptions_returns_correct_structure(self, pro_user_token):
        """Subscriptions returns active and canceled arrays with strategy details"""
        response = requests.get(
            f"{BASE_URL}/api/billing/subscriptions",
            headers={"Authorization": f"Bearer {pro_user_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify structure
        assert "active" in data, "Missing active array"
        assert "canceled" in data, "Missing canceled array"
        assert "active_count" in data, "Missing active_count"
        assert "total_count" in data, "Missing total_count"
        
        assert isinstance(data["active"], list), "active should be a list"
        assert isinstance(data["canceled"], list), "canceled should be a list"
        
        print(f"Subscriptions: {data['active_count']} active, {len(data['canceled'])} canceled, {data['total_count']} total")
        
        # Verify subscription object structure if any exist
        all_subs = data["active"] + data["canceled"]
        if all_subs:
            sub = all_subs[0]
            assert "id" in sub or "strategy_id" in sub, "Subscription missing id"
            assert "strategy_name" in sub, "Subscription missing strategy_name"
            assert "status" in sub, "Subscription missing status"
            print(f"Sample subscription: {sub.get('strategy_name')} - {sub.get('status')}")

    def test_billing_subscriptions_requires_auth(self):
        """Subscriptions endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/billing/subscriptions")
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"

    def test_billing_subscriptions_active_have_strategy_details(self, pro_user_token):
        """Active subscriptions include strategy details"""
        response = requests.get(
            f"{BASE_URL}/api/billing/subscriptions",
            headers={"Authorization": f"Bearer {pro_user_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        for sub in data.get("active", []):
            assert sub.get("status") == "active", f"Active sub has wrong status: {sub.get('status')}"
            # Strategy details may be in 'strategy' field
            if sub.get("strategy"):
                print(f"Active sub '{sub.get('strategy_name')}' has strategy details: {sub.get('strategy')}")


class TestBillingPayments:
    """Tests for GET /api/billing/payments endpoint"""

    def test_billing_payments_returns_correct_structure(self, pro_user_token):
        """Payments returns payments array with transaction details"""
        response = requests.get(
            f"{BASE_URL}/api/billing/payments",
            headers={"Authorization": f"Bearer {pro_user_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "payments" in data, "Missing payments array"
        assert "count" in data, "Missing count field"
        assert isinstance(data["payments"], list), "payments should be a list"
        
        print(f"Payments: {data['count']} transactions")
        
        # Verify payment object structure if any exist
        if data["payments"]:
            payment = data["payments"][0]
            assert "strategy_name" in payment, "Payment missing strategy_name"
            assert "amount" in payment, "Payment missing amount"
            assert "payment_status" in payment or "status" in payment, "Payment missing status"
            assert "created_at" in payment, "Payment missing created_at"
            print(f"Sample payment: {payment.get('strategy_name')} - ${payment.get('amount')} - {payment.get('payment_status')}")

    def test_billing_payments_requires_auth(self):
        """Payments endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/billing/payments")
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"


class TestTrackingEndpoint:
    """Tests for POST /api/admin/track endpoint (no auth required)"""

    def test_track_page_view_event(self):
        """Track endpoint accepts page_view events without auth"""
        response = requests.post(
            f"{BASE_URL}/api/admin/track",
            json={
                "event_type": "page_view",
                "metadata": {
                    "path": "/billing",
                    "referrer": "(direct)",
                    "user_agent": "pytest-test-agent"
                }
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("tracked") == True, "Expected tracked: true"
        print(f"Page view tracked, demo_mode: {data.get('demo_mode')}")

    def test_track_api_call_event(self):
        """Track endpoint accepts api_call events without auth"""
        response = requests.post(
            f"{BASE_URL}/api/admin/track",
            json={
                "event_type": "api_call",
                "metadata": {
                    "endpoint": "/api/billing/overview",
                    "method": "GET",
                    "status": 200,
                    "latency_ms": 150
                }
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("tracked") == True, "Expected tracked: true"
        print(f"API call tracked, demo_mode: {data.get('demo_mode')}")

    def test_track_custom_event(self):
        """Track endpoint accepts custom event types"""
        response = requests.post(
            f"{BASE_URL}/api/admin/track",
            json={
                "event_type": "billing_portal_opened",
                "metadata": {
                    "user_type": "pro",
                    "source": "my_strategies_page"
                }
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("tracked") == True
        print(f"Custom event tracked")

    def test_track_minimal_payload(self):
        """Track endpoint works with minimal payload"""
        response = requests.post(
            f"{BASE_URL}/api/admin/track",
            json={"event_type": "test_event"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("tracked") == True


class TestBillingIntegration:
    """Integration tests for billing data consistency"""

    def test_overview_matches_subscriptions_count(self, pro_user_token):
        """Overview active_subscriptions matches subscriptions active_count"""
        headers = {"Authorization": f"Bearer {pro_user_token}"}
        
        overview_res = requests.get(f"{BASE_URL}/api/billing/overview", headers=headers)
        subs_res = requests.get(f"{BASE_URL}/api/billing/subscriptions", headers=headers)
        
        assert overview_res.status_code == 200
        assert subs_res.status_code == 200
        
        overview = overview_res.json()
        subs = subs_res.json()
        
        assert overview["active_subscriptions"] == subs["active_count"], \
            f"Mismatch: overview has {overview['active_subscriptions']} but subscriptions has {subs['active_count']}"
        
        print(f"Consistency check passed: {overview['active_subscriptions']} active subscriptions")

    def test_monthly_cost_calculation(self, pro_user_token):
        """Monthly cost should be active_subscriptions * $9.99"""
        response = requests.get(
            f"{BASE_URL}/api/billing/overview",
            headers={"Authorization": f"Bearer {pro_user_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        expected_cost = round(data["active_subscriptions"] * 9.99, 2)
        actual_cost = data["monthly_cost"]
        
        assert actual_cost == expected_cost, \
            f"Monthly cost mismatch: expected ${expected_cost}, got ${actual_cost}"
        
        print(f"Monthly cost calculation correct: {data['active_subscriptions']} subs × $9.99 = ${actual_cost}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
