"""
Test Stripe Payment Integration for AlphaAI Platform

Endpoints tested:
- GET /api/payments/packages - Returns available subscription packages
- POST /api/payments/checkout - Creates Stripe checkout session
- GET /api/payments/status/{session_id} - Gets payment status
- GET /api/users/pro-status/{wallet_address} - Checks if user has Pro subscription
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestStripePaymentEndpoints:
    """Tests for Stripe Payment Integration"""
    
    def test_get_packages(self):
        """Test GET /api/payments/packages - Returns available subscription packages"""
        response = requests.get(f"{BASE_URL}/api/payments/packages")
        
        # Status assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert "packages" in data, "Response should contain 'packages' key"
        
        packages = data["packages"]
        assert len(packages) == 2, f"Expected 2 packages, got {len(packages)}"
        
        # Verify monthly package
        monthly_pkg = next((p for p in packages if p["id"] == "pro_monthly"), None)
        assert monthly_pkg is not None, "pro_monthly package should exist"
        assert monthly_pkg["price"] == 29.00, f"Monthly price should be 29, got {monthly_pkg['price']}"
        assert monthly_pkg["period"] == "month", f"Monthly period should be 'month'"
        assert monthly_pkg["currency"] == "usd", f"Currency should be 'usd'"
        
        # Verify yearly package
        yearly_pkg = next((p for p in packages if p["id"] == "pro_yearly"), None)
        assert yearly_pkg is not None, "pro_yearly package should exist"
        assert yearly_pkg["price"] == 249.00, f"Yearly price should be 249, got {yearly_pkg['price']}"
        assert yearly_pkg["period"] == "year", f"Yearly period should be 'year'"
        
        print("✅ GET /api/payments/packages - All assertions passed")
    
    def test_create_checkout_monthly(self):
        """Test POST /api/payments/checkout - Creates checkout session for monthly"""
        origin_url = "https://signal-lab-demo.preview.emergentagent.com"
        test_wallet = f"TEST_wallet_{uuid.uuid4().hex[:8]}"
        
        payload = {
            "package_id": "pro_monthly",
            "origin_url": origin_url,
            "wallet_address": test_wallet
        }
        
        response = requests.post(f"{BASE_URL}/api/payments/checkout", json=payload)
        
        # Status assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert "checkout_url" in data, "Response should contain 'checkout_url'"
        assert "session_id" in data, "Response should contain 'session_id'"
        assert "package" in data, "Response should contain 'package'"
        
        # Verify checkout_url starts with Stripe checkout
        checkout_url = data["checkout_url"]
        assert checkout_url.startswith("https://checkout.stripe.com/"), f"Checkout URL should start with Stripe, got: {checkout_url[:50]}"
        
        # Verify session_id format
        session_id = data["session_id"]
        assert session_id.startswith("cs_test_"), f"Session ID should start with 'cs_test_', got: {session_id[:20]}"
        
        # Verify package details
        package = data["package"]
        assert package["amount"] == 29.00, f"Monthly amount should be 29, got {package['amount']}"
        assert package["currency"] == "usd", f"Currency should be 'usd'"
        
        print(f"✅ POST /api/payments/checkout (monthly) - Checkout URL: {checkout_url[:50]}...")
        return session_id
    
    def test_create_checkout_yearly(self):
        """Test POST /api/payments/checkout - Creates checkout session for yearly"""
        origin_url = "https://signal-lab-demo.preview.emergentagent.com"
        test_wallet = f"TEST_wallet_{uuid.uuid4().hex[:8]}"
        
        payload = {
            "package_id": "pro_yearly",
            "origin_url": origin_url,
            "wallet_address": test_wallet
        }
        
        response = requests.post(f"{BASE_URL}/api/payments/checkout", json=payload)
        
        # Status assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert "checkout_url" in data, "Response should contain 'checkout_url'"
        assert "session_id" in data, "Response should contain 'session_id'"
        
        # Verify checkout_url starts with Stripe checkout
        checkout_url = data["checkout_url"]
        assert checkout_url.startswith("https://checkout.stripe.com/"), f"Checkout URL should start with Stripe"
        
        # Verify package details
        package = data["package"]
        assert package["amount"] == 249.00, f"Yearly amount should be 249, got {package['amount']}"
        
        print(f"✅ POST /api/payments/checkout (yearly) - Checkout URL: {checkout_url[:50]}...")
        return data["session_id"]
    
    def test_create_checkout_without_wallet(self):
        """Test POST /api/payments/checkout - Works without wallet address"""
        origin_url = "https://signal-lab-demo.preview.emergentagent.com"
        
        payload = {
            "package_id": "pro_monthly",
            "origin_url": origin_url
            # No wallet_address
        }
        
        response = requests.post(f"{BASE_URL}/api/payments/checkout", json=payload)
        
        # Status assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "checkout_url" in data, "Response should contain 'checkout_url' even without wallet"
        
        print("✅ POST /api/payments/checkout (no wallet) - Works for demo users")
    
    def test_create_checkout_invalid_package(self):
        """Test POST /api/payments/checkout - Invalid package returns error"""
        origin_url = "https://signal-lab-demo.preview.emergentagent.com"
        
        payload = {
            "package_id": "invalid_package",
            "origin_url": origin_url
        }
        
        response = requests.post(f"{BASE_URL}/api/payments/checkout", json=payload)
        
        # Should return 400 for invalid package
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "detail" in data, "Error response should have 'detail'"
        
        print("✅ POST /api/payments/checkout (invalid package) - Returns 400 error as expected")
    
    def test_get_payment_status(self):
        """Test GET /api/payments/status/{session_id} - Gets payment status"""
        # First create a checkout session to get a valid session_id
        origin_url = "https://signal-lab-demo.preview.emergentagent.com"
        test_wallet = f"TEST_wallet_{uuid.uuid4().hex[:8]}"
        
        checkout_payload = {
            "package_id": "pro_monthly",
            "origin_url": origin_url,
            "wallet_address": test_wallet
        }
        
        checkout_response = requests.post(f"{BASE_URL}/api/payments/checkout", json=checkout_payload)
        assert checkout_response.status_code == 200, f"Checkout failed: {checkout_response.text}"
        
        session_id = checkout_response.json()["session_id"]
        
        # Now get the payment status
        status_response = requests.get(f"{BASE_URL}/api/payments/status/{session_id}")
        
        # Status assertion
        assert status_response.status_code == 200, f"Expected 200, got {status_response.status_code}: {status_response.text}"
        
        # Data assertions
        data = status_response.json()
        assert "session_id" in data, "Response should contain 'session_id'"
        assert "status" in data, "Response should contain 'status'"
        assert "payment_status" in data, "Response should contain 'payment_status'"
        assert "is_pro" in data, "Response should contain 'is_pro'"
        
        # New session should be unpaid
        assert data["payment_status"] != "paid", "New session should not be paid yet"
        assert data["is_pro"] == False, "New session user should not be Pro yet"
        
        print(f"✅ GET /api/payments/status/{session_id[:20]}... - Status: {data['status']}, Payment: {data['payment_status']}")
    
    def test_get_payment_status_invalid_session(self):
        """Test GET /api/payments/status/{session_id} - Invalid session returns 404"""
        fake_session_id = "cs_test_invalid_session_12345"
        
        response = requests.get(f"{BASE_URL}/api/payments/status/{fake_session_id}")
        
        # Should return 404 for invalid session
        assert response.status_code == 404, f"Expected 404 for invalid session, got {response.status_code}: {response.text}"
        
        print("✅ GET /api/payments/status (invalid session) - Returns 404 as expected")
    
    def test_get_pro_status_nonexistent_user(self):
        """Test GET /api/users/pro-status/{wallet_address} - Non-existent user returns is_pro: false"""
        fake_wallet = f"0x{uuid.uuid4().hex}"  # Non-existent wallet
        
        response = requests.get(f"{BASE_URL}/api/users/pro-status/{fake_wallet}")
        
        # Status assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert "is_pro" in data, "Response should contain 'is_pro'"
        assert "wallet_address" in data, "Response should contain 'wallet_address'"
        assert data["is_pro"] == False, "Non-existent user should not be Pro"
        assert data["wallet_address"] == fake_wallet, "Wallet address should match"
        
        print("✅ GET /api/users/pro-status (non-existent) - Returns is_pro: false")
    
    def test_get_pro_status_existing_user(self):
        """Test GET /api/users/pro-status/{wallet_address} - Existing non-Pro user"""
        # First register an investor
        test_wallet = f"TEST_wallet_{uuid.uuid4().hex[:8]}"
        
        register_response = requests.post(f"{BASE_URL}/api/investors/register", json={
            "wallet_address": test_wallet
        })
        assert register_response.status_code == 200, f"Failed to register investor: {register_response.text}"
        
        # Now check pro status
        response = requests.get(f"{BASE_URL}/api/users/pro-status/{test_wallet}")
        
        # Status assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert data["is_pro"] == False, "Newly registered user should not be Pro"
        assert data["wallet_address"] == test_wallet
        
        print("✅ GET /api/users/pro-status (existing user) - Returns correct pro status")


class TestPaymentIntegrationFlow:
    """End-to-end payment flow tests"""
    
    def test_full_checkout_flow_creation(self):
        """Test complete checkout flow creation"""
        origin_url = "https://signal-lab-demo.preview.emergentagent.com"
        test_wallet = f"TEST_wallet_{uuid.uuid4().hex[:8]}"
        
        # Step 1: Get packages
        packages_response = requests.get(f"{BASE_URL}/api/payments/packages")
        assert packages_response.status_code == 200
        packages = packages_response.json()["packages"]
        print(f"  Step 1: Retrieved {len(packages)} packages")
        
        # Step 2: Create checkout for monthly
        checkout_payload = {
            "package_id": "pro_monthly",
            "origin_url": origin_url,
            "wallet_address": test_wallet
        }
        checkout_response = requests.post(f"{BASE_URL}/api/payments/checkout", json=checkout_payload)
        assert checkout_response.status_code == 200
        
        checkout_data = checkout_response.json()
        session_id = checkout_data["session_id"]
        checkout_url = checkout_data["checkout_url"]
        print(f"  Step 2: Created checkout session {session_id[:20]}...")
        
        # Step 3: Verify payment status is pending
        status_response = requests.get(f"{BASE_URL}/api/payments/status/{session_id}")
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data["is_pro"] == False, "User should not be Pro until payment completes"
        print(f"  Step 3: Verified payment status - not yet paid")
        
        # Step 4: Verify user is not Pro yet
        pro_status_response = requests.get(f"{BASE_URL}/api/users/pro-status/{test_wallet}")
        assert pro_status_response.status_code == 200
        assert pro_status_response.json()["is_pro"] == False
        print(f"  Step 4: Verified user is not Pro yet")
        
        print("✅ Full checkout flow creation test passed")
        print(f"  Checkout URL: {checkout_url}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
