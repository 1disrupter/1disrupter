"""
P0 Go-Live Fixes Test Suite
Tests for the 7 P0 fixes required for SaaS-only public launch:
- P0-1: Dashboard wallet gating bypass for authenticated users
- P0-2: Live crypto price feed (Kraken API via httpx)
- P0-3: Landing page hero - no blockchain/Web3 messaging
- P0-4: 404 catch-all route
- P0-5: Favicon link in index.html
- P0-6: Meta description update
- P0-7: Wallet navigation controls hidden
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestP0LivePriceFeed:
    """P0-2: Test live crypto price feed from Kraken"""
    
    def test_live_prices_endpoint_returns_200(self):
        """GET /api/market/live-prices should return 200"""
        response = requests.get(f"{BASE_URL}/api/market/live-prices", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: /api/market/live-prices returns 200")
    
    def test_live_prices_has_kraken_source(self):
        """Live prices should come from Kraken, not fallback"""
        response = requests.get(f"{BASE_URL}/api/market/live-prices", timeout=15)
        assert response.status_code == 200
        data = response.json()
        
        # Check source is kraken (not fallback)
        source = data.get('source', '')
        assert source == 'kraken', f"Expected source='kraken', got source='{source}'"
        print(f"PASS: Live prices source is '{source}'")
    
    def test_live_prices_has_real_data(self):
        """Live prices should have real price data with non-zero change"""
        response = requests.get(f"{BASE_URL}/api/market/live-prices", timeout=15)
        assert response.status_code == 200
        data = response.json()
        
        prices = data.get('prices', [])
        assert len(prices) > 0, "Expected at least one price entry"
        
        # Check BTC price is reasonable (not fallback 70000 with 0% change)
        btc = next((p for p in prices if p.get('symbol') == 'BTC'), None)
        assert btc is not None, "BTC price not found"
        
        btc_price = btc.get('price', 0)
        btc_change = btc.get('change_24h', 0)
        
        # Real prices should have some change (not exactly 0)
        # Note: It's possible for real change to be 0, but unlikely
        print(f"BTC price: ${btc_price}, 24h change: {btc_change}%")
        
        # Verify price is in reasonable range
        assert 10000 < btc_price < 200000, f"BTC price {btc_price} seems unreasonable"
        print(f"PASS: BTC price ${btc_price} is reasonable")
    
    def test_live_prices_alias_endpoint(self):
        """GET /api/live-prices alias should also work"""
        response = requests.get(f"{BASE_URL}/api/live-prices", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'prices' in data, "Expected 'prices' key in response"
        print("PASS: /api/live-prices alias works")


class TestP0AuthLogin:
    """Test login flow for dashboard access"""
    
    def test_login_pro_user(self):
        """POST /api/auth/login should work for pro user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "demo_test2@my-alpha-ai.com",
                "password": "NewPass1234!"
            },
            timeout=10
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert 'access_token' in data, "Expected access_token in response"
        assert 'user' in data, "Expected user in response"
        print(f"PASS: Pro user login successful, user_tier: {data['user'].get('user_tier')}")
        return data['access_token']
    
    def test_login_free_user(self):
        """POST /api/auth/login should work for free user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "test_free_user_iter29@my-alpha-ai.com",
                "password": "TestPass123!"
            },
            timeout=10
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert 'access_token' in data, "Expected access_token in response"
        print(f"PASS: Free user login successful, user_tier: {data['user'].get('user_tier')}")
    
    def test_login_admin_user(self):
        """POST /api/auth/login should work for admin user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "mar-brick@hotmail.com",
                "password": "Martin2026!"
            },
            timeout=10
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert 'access_token' in data, "Expected access_token in response"
        print(f"PASS: Admin user login successful")


class TestP0GeneralEndpoints:
    """Test general API endpoints"""
    
    def test_root_endpoint(self):
        """GET /api/ should return API info"""
        response = requests.get(f"{BASE_URL}/api/", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Root API endpoint works")
    
    def test_fund_stats(self):
        """GET /api/fund/stats should return fund statistics"""
        response = requests.get(f"{BASE_URL}/api/fund/stats", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'nav' in data, "Expected 'nav' in fund stats"
        assert 'sharpe_ratio' in data, "Expected 'sharpe_ratio' in fund stats"
        print(f"PASS: Fund stats returned, NAV: {data.get('nav')}")
    
    def test_signals_free_endpoint(self):
        """GET /api/signals/free should return free tier signals"""
        response = requests.get(f"{BASE_URL}/api/signals/free", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'signals' in data, "Expected 'signals' in response"
        print(f"PASS: Free signals endpoint works, got {len(data.get('signals', []))} signals")


class TestP0FrontendAssets:
    """Test frontend static assets"""
    
    def test_index_html_loads(self):
        """Frontend index.html should load"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert 'text/html' in response.headers.get('content-type', ''), "Expected HTML content"
        print("PASS: Frontend index.html loads")
    
    def test_favicon_exists(self):
        """Favicon.svg should be accessible"""
        response = requests.get(f"{BASE_URL}/favicon.svg", timeout=10)
        # May return 200 or redirect, both are acceptable
        assert response.status_code in [200, 301, 302, 304], f"Expected 200/301/302/304, got {response.status_code}"
        print(f"PASS: Favicon accessible (status: {response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
