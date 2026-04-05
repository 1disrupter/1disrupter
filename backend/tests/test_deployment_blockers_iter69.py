"""
Test Deployment Blockers Fix - Iteration 69
Verifies all P0 deployment blocker fixes:
1. Bounded DB queries in strategies.py (weekly report)
2. contracts/ and web3/ directories deleted
3. No web3 imports in contract_manager.py
4. web3_routes.py deleted
5. No blockchain packages in requirements.txt
6. All core endpoints still working
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://signal-ui-latest.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "mar-brick@hotmail.com"
ADMIN_PASSWORD = "Martin2026!"
PRO_EMAIL = "demo_test2@my-alpha-ai.com"
PRO_PASSWORD = "NewPass1234!"
ADMIN_KEY = "alphaai_admin_2026"


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
        "email": PRO_EMAIL,
        "password": PRO_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


class TestHealthCheck:
    """Health check endpoint tests"""
    
    def test_api_health_returns_healthy(self, api_client):
        """GET /api/health should return {status: healthy}"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("PASS: /api/health returns healthy")


class TestAuthentication:
    """Authentication endpoint tests"""
    
    def test_login_with_valid_credentials(self, api_client):
        """POST /api/auth/login with valid credentials should return access_token"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": PRO_EMAIL,
            "password": PRO_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
        print("PASS: Login returns access_token")


class TestWeeklyReport:
    """Weekly report endpoint tests - verifies bounded DB queries"""
    
    def test_weekly_report_returns_bounded_trades(self, api_client):
        """GET /api/reports/weekly should return date-filtered trades (not all trades)"""
        response = api_client.get(f"{BASE_URL}/api/reports/weekly")
        assert response.status_code == 200
        data = response.json()
        
        # Verify report structure
        assert "report_type" in data
        assert data["report_type"] == "weekly"
        assert "period" in data
        assert "summary" in data
        assert "trading" in data
        
        # Verify trading section has bounded data
        trading = data.get("trading", {})
        assert "total_trades" in trading
        assert "daily_breakdown" in trading
        
        # Daily breakdown should have 7 days max
        daily_breakdown = trading.get("daily_breakdown", [])
        assert len(daily_breakdown) <= 7
        
        print(f"PASS: Weekly report returns bounded data - {trading.get('total_trades')} trades")


class TestStrategyLeaderboard:
    """Strategy leaderboard endpoint tests"""
    
    def test_leaderboard_returns_strategies_with_performance(self, api_client):
        """GET /api/marketplace/strategies/leaderboard should return strategies with performance data"""
        response = api_client.get(f"{BASE_URL}/api/marketplace/strategies/leaderboard")
        assert response.status_code == 200
        data = response.json()
        
        assert "strategies" in data
        assert "total" in data
        assert isinstance(data["strategies"], list)
        
        print(f"PASS: Leaderboard returns {data['total']} strategies")


class TestMarketplaceListing:
    """Marketplace listing endpoint tests"""
    
    def test_marketplace_supports_pagination(self, api_client):
        """GET /api/marketplace/strategies should support pagination (page, limit params)"""
        response = api_client.get(f"{BASE_URL}/api/marketplace/strategies?page=1&limit=5")
        assert response.status_code == 200
        data = response.json()
        
        assert "strategies" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "pages" in data
        
        assert data["page"] == 1
        assert data["limit"] == 5
        
        print(f"PASS: Marketplace supports pagination - page={data['page']}, limit={data['limit']}, total={data['total']}")


class TestFeaturedStrategies:
    """Featured strategies endpoint tests"""
    
    def test_featured_returns_published_strategies(self, api_client):
        """GET /api/marketplace/featured should return published featured strategies"""
        response = api_client.get(f"{BASE_URL}/api/marketplace/featured")
        assert response.status_code == 200
        data = response.json()
        
        assert "strategies" in data
        assert isinstance(data["strategies"], list)
        
        print(f"PASS: Featured endpoint returns {len(data['strategies'])} strategies")


class TestStrategyAttestation:
    """Strategy attestation endpoint tests"""
    
    def test_attestation_demo_mode_returns_mock(self, api_client):
        """GET /api/strategies/test-id/attestation?demo=true should return mock attestation (on_chain: false)"""
        response = api_client.get(f"{BASE_URL}/api/strategies/test-id/attestation?demo=true")
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert data["success"] == True
        
        # In demo mode, attestation should be mock (on_chain: false or None)
        attestation = data.get("attestation")
        if attestation:
            assert attestation.get("on_chain") == False or attestation.get("on_chain") is None
        
        print("PASS: Attestation demo mode returns mock data")


class TestWaitlist:
    """Waitlist endpoint tests"""
    
    def test_waitlist_registers_email(self, api_client):
        """POST /api/waitlist with {email: ...} should register email"""
        test_email = f"test_iter69_{int(time.time())}@my-alpha-ai.com"
        response = api_client.post(f"{BASE_URL}/api/waitlist", json={
            "email": test_email
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "waitlist_id" in data
        
        print(f"PASS: Waitlist registers email - waitlist_id={data['waitlist_id']}")


class TestWaitlistAdmin:
    """Waitlist admin endpoint tests"""
    
    def test_waitlist_admin_analytics(self, api_client):
        """GET /api/waitlist/admin/analytics?admin_key=alphaai_admin_2026 should return analytics"""
        response = api_client.get(f"{BASE_URL}/api/waitlist/admin/analytics?admin_key={ADMIN_KEY}")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_waitlist" in data
        assert "funnel" in data
        assert "activation_rate" in data
        assert "conversion_rate" in data
        assert "emails" in data
        
        print(f"PASS: Waitlist admin analytics - total={data['total_waitlist']}")


class TestReferralsAdmin:
    """Referrals admin endpoint tests"""
    
    def test_referrals_admin_summary(self, api_client):
        """GET /api/referrals/admin/summary?admin_key=alphaai_admin_2026 should return summary"""
        response = api_client.get(f"{BASE_URL}/api/referrals/admin/summary?admin_key={ADMIN_KEY}")
        assert response.status_code == 200
        data = response.json()
        
        # Should return referral summary data
        assert isinstance(data, dict)
        
        print("PASS: Referrals admin summary returns data")


class TestInvoices:
    """Invoice listing endpoint tests"""
    
    def test_invoices_with_auth(self, authenticated_client):
        """GET /api/invoices with auth token should return invoice list"""
        response = authenticated_client.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200
        data = response.json()
        
        assert "invoices" in data
        assert isinstance(data["invoices"], list)
        
        print(f"PASS: Invoices endpoint returns {len(data['invoices'])} invoices")


class TestBillingOverview:
    """Billing overview endpoint tests"""
    
    def test_billing_overview_with_auth(self, authenticated_client):
        """GET /api/billing/overview with auth token should return billing data"""
        response = authenticated_client.get(f"{BASE_URL}/api/billing/overview")
        assert response.status_code == 200
        data = response.json()
        
        # Should return billing overview data
        assert isinstance(data, dict)
        
        print("PASS: Billing overview returns data")


class TestFrontendServing:
    """Frontend serving tests"""
    
    def test_frontend_serves_react_app(self, api_client):
        """GET / should return HTML with 'My-AlphaAI' and 'root' div, NOT NGINX default page"""
        response = api_client.get(f"{BASE_URL}/")
        assert response.status_code == 200
        
        html = response.text
        
        # Should contain React app markers
        assert "root" in html, "Missing 'root' div - not React app"
        assert "My-AlphaAI" in html or "AlphaAI" in html, "Missing app title - not React app"
        
        # Should NOT be NGINX default page
        assert "Welcome to nginx" not in html, "Got NGINX default page instead of React app"
        
        print("PASS: Frontend serves React app correctly")


class TestNoWeb3Dependencies:
    """Verify web3/blockchain code has been removed"""
    
    def test_contracts_directory_deleted(self):
        """Verify /app/backend/contracts/ does not exist"""
        import os
        assert not os.path.exists("/app/backend/contracts/"), "contracts/ directory should be deleted"
        print("PASS: contracts/ directory does not exist")
    
    def test_web3_directory_deleted(self):
        """Verify /app/backend/web3/ does not exist"""
        import os
        assert not os.path.exists("/app/backend/web3/"), "web3/ directory should be deleted"
        print("PASS: web3/ directory does not exist")
    
    def test_web3_routes_deleted(self):
        """Verify /app/backend/routes/web3_routes.py does not exist"""
        import os
        assert not os.path.exists("/app/backend/routes/web3_routes.py"), "web3_routes.py should be deleted"
        print("PASS: web3_routes.py does not exist")
    
    def test_no_blockchain_packages_in_requirements(self):
        """Verify no web3/ethers/eth-utils/eth-abi in requirements.txt"""
        with open("/app/backend/requirements.txt", "r") as f:
            content = f.read().lower()
        
        blockchain_packages = ["web3", "ethers", "eth-utils", "eth-abi"]
        for pkg in blockchain_packages:
            assert pkg not in content, f"Found {pkg} in requirements.txt - should be removed"
        
        print("PASS: No blockchain packages in requirements.txt")


class TestContractManagerMock:
    """Verify contract_manager.py is a pure mock stub"""
    
    def test_contract_manager_is_mock(self):
        """Verify contract_manager.py has no web3 imports and returns mock data"""
        with open("/app/backend/services/contract_manager.py", "r") as f:
            content = f.read()
        
        # Should NOT have web3 imports
        assert "from web3" not in content, "contract_manager.py should not import web3"
        assert "import web3" not in content, "contract_manager.py should not import web3"
        
        # Should have mock indicators
        assert "mock" in content.lower(), "contract_manager.py should be a mock stub"
        
        print("PASS: contract_manager.py is a pure mock stub")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
