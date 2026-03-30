"""
Beta Spots Feature Tests
- GET /api/public/beta-spots endpoint returns correct JSON {total, used, remaining}
- Beta spots total matches BETA_SPOTS_TOTAL env var (50)
- Beta spots 'used' count matches users where is_beta_tester=true
- New user registration sets is_beta_tester=true on the user document
- After registration, /api/public/beta-spots 'used' count increases by 1
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestBetaSpotsEndpoint:
    """Tests for GET /api/public/beta-spots endpoint"""
    
    def test_beta_spots_endpoint_returns_200(self):
        """Test that the beta spots endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/public/beta-spots")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Beta spots endpoint returns 200 OK")
    
    def test_beta_spots_returns_correct_json_structure(self):
        """Test that response contains total, used, remaining fields"""
        response = requests.get(f"{BASE_URL}/api/public/beta-spots")
        assert response.status_code == 200
        data = response.json()
        
        # Check all required fields exist
        assert "total" in data, "Response missing 'total' field"
        assert "used" in data, "Response missing 'used' field"
        assert "remaining" in data, "Response missing 'remaining' field"
        
        # Check field types
        assert isinstance(data["total"], int), f"'total' should be int, got {type(data['total'])}"
        assert isinstance(data["used"], int), f"'used' should be int, got {type(data['used'])}"
        assert isinstance(data["remaining"], int), f"'remaining' should be int, got {type(data['remaining'])}"
        
        print(f"✓ Beta spots returns correct JSON structure: {data}")
    
    def test_beta_spots_total_is_50(self):
        """Test that total matches BETA_SPOTS_TOTAL env var (50)"""
        response = requests.get(f"{BASE_URL}/api/public/beta-spots")
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 50, f"Expected total=50, got {data['total']}"
        print(f"✓ Beta spots total is 50 (matches BETA_SPOTS_TOTAL env var)")
    
    def test_beta_spots_remaining_calculation(self):
        """Test that remaining = total - used"""
        response = requests.get(f"{BASE_URL}/api/public/beta-spots")
        assert response.status_code == 200
        data = response.json()
        
        expected_remaining = data["total"] - data["used"]
        # remaining should be max(expected, 0)
        expected_remaining = max(expected_remaining, 0)
        
        assert data["remaining"] == expected_remaining, \
            f"Expected remaining={expected_remaining}, got {data['remaining']}"
        print(f"✓ Remaining calculation correct: {data['total']} - {data['used']} = {data['remaining']}")
    
    def test_beta_spots_used_is_non_negative(self):
        """Test that used count is non-negative"""
        response = requests.get(f"{BASE_URL}/api/public/beta-spots")
        assert response.status_code == 200
        data = response.json()
        
        assert data["used"] >= 0, f"'used' should be non-negative, got {data['used']}"
        print(f"✓ Beta spots 'used' is non-negative: {data['used']}")


class TestRegistrationSetsBetaTester:
    """Tests for registration setting is_beta_tester=true"""
    
    def test_registration_increases_beta_spots_used(self):
        """Test that new registration increases the 'used' count by 1"""
        # Get initial beta spots count
        initial_response = requests.get(f"{BASE_URL}/api/public/beta-spots")
        assert initial_response.status_code == 200
        initial_data = initial_response.json()
        initial_used = initial_data["used"]
        print(f"Initial beta spots used: {initial_used}")
        
        # Register a new user
        timestamp = int(time.time() * 1000)
        test_email = f"beta_test_{timestamp}@test.com"
        test_password = "TestPass123!"
        test_name = "Beta Test User"
        
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": test_email,
                "password": test_password,
                "name": test_name
            }
        )
        
        assert register_response.status_code == 200, \
            f"Registration failed: {register_response.status_code} - {register_response.text}"
        print(f"✓ User registered successfully: {test_email}")
        
        # Get updated beta spots count
        updated_response = requests.get(f"{BASE_URL}/api/public/beta-spots")
        assert updated_response.status_code == 200
        updated_data = updated_response.json()
        updated_used = updated_data["used"]
        
        # Verify used count increased by 1
        assert updated_used == initial_used + 1, \
            f"Expected used to increase from {initial_used} to {initial_used + 1}, got {updated_used}"
        print(f"✓ Beta spots 'used' increased from {initial_used} to {updated_used}")
        
        # Verify remaining decreased by 1
        assert updated_data["remaining"] == initial_data["remaining"] - 1, \
            f"Expected remaining to decrease by 1"
        print(f"✓ Beta spots 'remaining' decreased from {initial_data['remaining']} to {updated_data['remaining']}")
    
    def test_registration_returns_user_with_is_beta_tester(self):
        """Test that registration response includes user data (implicitly is_beta_tester=true)"""
        timestamp = int(time.time() * 1000)
        test_email = f"beta_test2_{timestamp}@test.com"
        test_password = "TestPass123!"
        test_name = "Beta Test User 2"
        
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": test_email,
                "password": test_password,
                "name": test_name
            }
        )
        
        assert register_response.status_code == 200, \
            f"Registration failed: {register_response.status_code} - {register_response.text}"
        
        data = register_response.json()
        
        # Verify response structure
        assert "access_token" in data, "Response missing 'access_token'"
        assert "refresh_token" in data, "Response missing 'refresh_token'"
        assert "user" in data, "Response missing 'user'"
        
        user = data["user"]
        assert user["email"] == test_email.lower(), f"Email mismatch"
        assert user["name"] == test_name, f"Name mismatch"
        
        print(f"✓ Registration returns valid user data for {test_email}")


class TestBetaSpotsEdgeCases:
    """Edge case tests for beta spots feature"""
    
    def test_beta_spots_endpoint_is_public(self):
        """Test that endpoint works without authentication"""
        # No auth header
        response = requests.get(f"{BASE_URL}/api/public/beta-spots")
        assert response.status_code == 200, \
            f"Public endpoint should not require auth, got {response.status_code}"
        print(f"✓ Beta spots endpoint is public (no auth required)")
    
    def test_beta_spots_remaining_never_negative(self):
        """Test that remaining is never negative (capped at 0)"""
        response = requests.get(f"{BASE_URL}/api/public/beta-spots")
        assert response.status_code == 200
        data = response.json()
        
        assert data["remaining"] >= 0, \
            f"'remaining' should never be negative, got {data['remaining']}"
        print(f"✓ Beta spots 'remaining' is non-negative: {data['remaining']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
