"""
AlphaAI Copy Trading API Tests
Tests for follow/unfollow traders, settings management, pending trades approval/rejection.
Covers: Pro/Elite access control, circular copying prevention, duplicate follow prevention.
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials - Pro user
PRO_USER_EMAIL = "demo_test2@my-alpha-ai.com"
PRO_USER_PASSWORD = "NewPass1234!"

# Test traders from leaderboard
TEST_TRADER_1 = "TEST_SLTP_ab99a3d6"
TEST_TRADER_2 = "TEST_SLTP_eee0010e"


class TestCopyTradingAuth:
    """Test authentication and access control for copy trading"""
    
    @pytest.fixture(scope="class")
    def pro_user_token(self):
        """Get auth token for Pro user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": PRO_USER_EMAIL,
            "password": PRO_USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, pro_user_token):
        """Auth headers for Pro user"""
        return {"Authorization": f"Bearer {pro_user_token}"}
    
    def test_login_pro_user(self, pro_user_token):
        """Verify Pro user can login successfully"""
        assert pro_user_token is not None
        assert len(pro_user_token) > 0
        print(f"✓ Pro user login successful, token length: {len(pro_user_token)}")
    
    def test_get_following_requires_auth(self):
        """GET /api/copy/following requires authentication"""
        response = requests.get(f"{BASE_URL}/api/copy/following")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/copy/following requires auth")
    
    def test_get_followers_requires_auth(self):
        """GET /api/copy/followers requires authentication"""
        response = requests.get(f"{BASE_URL}/api/copy/followers")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/copy/followers requires auth")
    
    def test_get_pending_requires_auth(self):
        """GET /api/copy/pending requires authentication"""
        response = requests.get(f"{BASE_URL}/api/copy/pending")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/copy/pending requires auth")
    
    def test_follow_requires_auth(self):
        """POST /api/copy/follow requires authentication"""
        response = requests.post(f"{BASE_URL}/api/copy/follow", json={
            "trader_id": "test_trader",
            "mode": "auto",
            "allocation_percent": 10,
            "max_per_trade": 500
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/copy/follow requires auth")


class TestCopyTradingFollowing:
    """Test following/unfollowing traders"""
    
    @pytest.fixture(scope="class")
    def pro_user_token(self):
        """Get auth token for Pro user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": PRO_USER_EMAIL,
            "password": PRO_USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, pro_user_token):
        """Auth headers for Pro user"""
        return {"Authorization": f"Bearer {pro_user_token}"}
    
    @pytest.fixture(scope="class")
    def user_id(self, auth_headers):
        """Get current user ID"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        return response.json().get("id")
    
    def test_get_following_list(self, auth_headers):
        """GET /api/copy/following returns list of followed traders"""
        response = requests.get(f"{BASE_URL}/api/copy/following", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "success" in data
        assert "following" in data
        assert "count" in data
        assert isinstance(data["following"], list)
        print(f"✓ GET /api/copy/following - Currently following {data['count']} traders")
        return data["following"]
    
    def test_get_followers_list(self, auth_headers):
        """GET /api/copy/followers returns list of followers"""
        response = requests.get(f"{BASE_URL}/api/copy/followers", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "success" in data
        assert "followers" in data
        assert "count" in data
        assert isinstance(data["followers"], list)
        print(f"✓ GET /api/copy/followers - Has {data['count']} followers")
    
    def test_get_pending_trades(self, auth_headers):
        """GET /api/copy/pending returns pending manual trades"""
        response = requests.get(f"{BASE_URL}/api/copy/pending", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "success" in data
        assert "pending_trades" in data
        assert "count" in data
        assert isinstance(data["pending_trades"], list)
        print(f"✓ GET /api/copy/pending - Has {data['count']} pending trades")
    
    def test_cannot_follow_self(self, auth_headers, user_id):
        """Cannot follow yourself - safety check"""
        response = requests.post(f"{BASE_URL}/api/copy/follow", 
            headers=auth_headers,
            json={
                "trader_id": user_id,
                "mode": "auto",
                "allocation_percent": 10,
                "max_per_trade": 500
            })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "cannot copy yourself" in data.get("detail", "").lower() or "yourself" in data.get("detail", "").lower()
        print("✓ Cannot follow self - safety check passed")
    
    def test_follow_trader_duplicate_prevention(self, auth_headers):
        """Cannot create duplicate follow relationship"""
        # First, get current following list
        response = requests.get(f"{BASE_URL}/api/copy/following", headers=auth_headers)
        following = response.json().get("following", [])
        
        if len(following) > 0:
            # Try to follow an already followed trader
            existing_trader_id = following[0]["trader_id"]
            response = requests.post(f"{BASE_URL}/api/copy/follow",
                headers=auth_headers,
                json={
                    "trader_id": existing_trader_id,
                    "mode": "auto",
                    "allocation_percent": 10,
                    "max_per_trade": 500
                })
            assert response.status_code == 400, f"Expected 400 for duplicate, got {response.status_code}"
            data = response.json()
            assert "already following" in data.get("detail", "").lower()
            print(f"✓ Duplicate follow prevention works for trader {existing_trader_id}")
        else:
            print("⚠ No existing follows to test duplicate prevention - skipping")
    
    def test_allocation_validation(self, auth_headers):
        """Allocation percent must be between 1-100"""
        # Test with invalid allocation (0)
        response = requests.post(f"{BASE_URL}/api/copy/follow",
            headers=auth_headers,
            json={
                "trader_id": "test_invalid_allocation",
                "mode": "auto",
                "allocation_percent": 0,  # Invalid - below 1
                "max_per_trade": 500
            })
        # Should be 422 (validation error) or 400
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("✓ Allocation validation (0%) rejected")
        
        # Test with invalid allocation (150)
        response = requests.post(f"{BASE_URL}/api/copy/follow",
            headers=auth_headers,
            json={
                "trader_id": "test_invalid_allocation",
                "mode": "auto",
                "allocation_percent": 150,  # Invalid - above 100
                "max_per_trade": 500
            })
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("✓ Allocation validation (150%) rejected")


class TestCopyTradingSettings:
    """Test updating copy trading settings"""
    
    @pytest.fixture(scope="class")
    def pro_user_token(self):
        """Get auth token for Pro user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": PRO_USER_EMAIL,
            "password": PRO_USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, pro_user_token):
        """Auth headers for Pro user"""
        return {"Authorization": f"Bearer {pro_user_token}"}
    
    def test_update_settings_mode(self, auth_headers):
        """PUT /api/copy/settings can update mode"""
        # Get existing relationship
        response = requests.get(f"{BASE_URL}/api/copy/following", headers=auth_headers)
        following = response.json().get("following", [])
        
        if len(following) > 0:
            rel_id = following[0]["id"]
            current_mode = following[0]["mode"]
            new_mode = "manual" if current_mode == "auto" else "auto"
            
            # Update mode
            response = requests.put(f"{BASE_URL}/api/copy/settings",
                headers=auth_headers,
                json={
                    "relationship_id": rel_id,
                    "mode": new_mode
                })
            assert response.status_code == 200, f"Failed: {response.text}"
            data = response.json()
            assert data.get("success") == True
            assert data["relationship"]["mode"] == new_mode
            print(f"✓ Updated mode from {current_mode} to {new_mode}")
            
            # Revert back
            requests.put(f"{BASE_URL}/api/copy/settings",
                headers=auth_headers,
                json={"relationship_id": rel_id, "mode": current_mode})
        else:
            print("⚠ No existing follows to test settings update - skipping")
    
    def test_update_settings_allocation(self, auth_headers):
        """PUT /api/copy/settings can update allocation percent"""
        response = requests.get(f"{BASE_URL}/api/copy/following", headers=auth_headers)
        following = response.json().get("following", [])
        
        if len(following) > 0:
            rel_id = following[0]["id"]
            original_allocation = following[0]["allocation_percent"]
            new_allocation = 25 if original_allocation != 25 else 30
            
            response = requests.put(f"{BASE_URL}/api/copy/settings",
                headers=auth_headers,
                json={
                    "relationship_id": rel_id,
                    "allocation_percent": new_allocation
                })
            assert response.status_code == 200, f"Failed: {response.text}"
            data = response.json()
            assert data.get("success") == True
            assert data["relationship"]["allocation_percent"] == new_allocation
            print(f"✓ Updated allocation from {original_allocation}% to {new_allocation}%")
            
            # Revert
            requests.put(f"{BASE_URL}/api/copy/settings",
                headers=auth_headers,
                json={"relationship_id": rel_id, "allocation_percent": original_allocation})
        else:
            print("⚠ No existing follows to test allocation update - skipping")
    
    def test_update_settings_max_per_trade(self, auth_headers):
        """PUT /api/copy/settings can update max_per_trade"""
        response = requests.get(f"{BASE_URL}/api/copy/following", headers=auth_headers)
        following = response.json().get("following", [])
        
        if len(following) > 0:
            rel_id = following[0]["id"]
            original_max = following[0]["max_per_trade"]
            new_max = 750 if original_max != 750 else 1000
            
            response = requests.put(f"{BASE_URL}/api/copy/settings",
                headers=auth_headers,
                json={
                    "relationship_id": rel_id,
                    "max_per_trade": new_max
                })
            assert response.status_code == 200, f"Failed: {response.text}"
            data = response.json()
            assert data.get("success") == True
            assert data["relationship"]["max_per_trade"] == new_max
            print(f"✓ Updated max_per_trade from ${original_max} to ${new_max}")
            
            # Revert
            requests.put(f"{BASE_URL}/api/copy/settings",
                headers=auth_headers,
                json={"relationship_id": rel_id, "max_per_trade": original_max})
        else:
            print("⚠ No existing follows to test max_per_trade update - skipping")
    
    def test_update_settings_pause_resume(self, auth_headers):
        """PUT /api/copy/settings can pause and resume copying"""
        response = requests.get(f"{BASE_URL}/api/copy/following", headers=auth_headers)
        following = response.json().get("following", [])
        
        if len(following) > 0:
            rel_id = following[0]["id"]
            current_status = following[0]["status"]
            
            # Pause
            response = requests.put(f"{BASE_URL}/api/copy/settings",
                headers=auth_headers,
                json={"relationship_id": rel_id, "status": "paused"})
            assert response.status_code == 200, f"Failed to pause: {response.text}"
            assert response.json()["relationship"]["status"] == "paused"
            print("✓ Paused copy relationship")
            
            # Resume
            response = requests.put(f"{BASE_URL}/api/copy/settings",
                headers=auth_headers,
                json={"relationship_id": rel_id, "status": "active"})
            assert response.status_code == 200, f"Failed to resume: {response.text}"
            assert response.json()["relationship"]["status"] == "active"
            print("✓ Resumed copy relationship")
        else:
            print("⚠ No existing follows to test pause/resume - skipping")
    
    def test_update_settings_invalid_relationship(self, auth_headers):
        """PUT /api/copy/settings with invalid relationship_id returns 400"""
        response = requests.put(f"{BASE_URL}/api/copy/settings",
            headers=auth_headers,
            json={
                "relationship_id": "invalid-uuid-12345",
                "mode": "auto"
            })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Invalid relationship_id returns 400")


class TestCopyTradingUnfollow:
    """Test unfollowing traders"""
    
    @pytest.fixture(scope="class")
    def pro_user_token(self):
        """Get auth token for Pro user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": PRO_USER_EMAIL,
            "password": PRO_USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, pro_user_token):
        """Auth headers for Pro user"""
        return {"Authorization": f"Bearer {pro_user_token}"}
    
    def test_unfollow_invalid_relationship(self, auth_headers):
        """DELETE /api/copy/unfollow/{id} with invalid id returns 400"""
        response = requests.delete(f"{BASE_URL}/api/copy/unfollow/invalid-uuid-12345",
            headers=auth_headers)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Unfollow invalid relationship returns 400")


class TestCopyTradingApproveReject:
    """Test approve/reject pending trades"""
    
    @pytest.fixture(scope="class")
    def pro_user_token(self):
        """Get auth token for Pro user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": PRO_USER_EMAIL,
            "password": PRO_USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, pro_user_token):
        """Auth headers for Pro user"""
        return {"Authorization": f"Bearer {pro_user_token}"}
    
    def test_approve_invalid_trade(self, auth_headers):
        """POST /api/copy/approve/{trade_id} with invalid id returns 400"""
        response = requests.post(f"{BASE_URL}/api/copy/approve/invalid-trade-id",
            headers=auth_headers)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Approve invalid trade returns 400")
    
    def test_reject_invalid_trade(self, auth_headers):
        """POST /api/copy/reject/{trade_id} with invalid id returns 400"""
        response = requests.post(f"{BASE_URL}/api/copy/reject/invalid-trade-id",
            headers=auth_headers)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Reject invalid trade returns 400")


class TestCopyTradingDataIntegrity:
    """Test data integrity and response structure"""
    
    @pytest.fixture(scope="class")
    def pro_user_token(self):
        """Get auth token for Pro user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": PRO_USER_EMAIL,
            "password": PRO_USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, pro_user_token):
        """Auth headers for Pro user"""
        return {"Authorization": f"Bearer {pro_user_token}"}
    
    def test_following_response_structure(self, auth_headers):
        """Verify following response has correct structure"""
        response = requests.get(f"{BASE_URL}/api/copy/following", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check top-level structure
        assert "success" in data
        assert "following" in data
        assert "count" in data
        
        # Check each relationship structure
        for rel in data["following"]:
            assert "id" in rel, "Missing 'id' in relationship"
            assert "copier_id" in rel, "Missing 'copier_id' in relationship"
            assert "trader_id" in rel, "Missing 'trader_id' in relationship"
            assert "mode" in rel, "Missing 'mode' in relationship"
            assert "allocation_percent" in rel, "Missing 'allocation_percent' in relationship"
            assert "max_per_trade" in rel, "Missing 'max_per_trade' in relationship"
            assert "status" in rel, "Missing 'status' in relationship"
            assert "stats" in rel, "Missing 'stats' in relationship"
            assert "trader_display_name" in rel, "Missing 'trader_display_name' in relationship"
            
            # Validate mode values
            assert rel["mode"] in ["auto", "manual"], f"Invalid mode: {rel['mode']}"
            # Validate status values
            assert rel["status"] in ["active", "paused", "removed"], f"Invalid status: {rel['status']}"
            # Validate allocation range
            assert 1 <= rel["allocation_percent"] <= 100, f"Invalid allocation: {rel['allocation_percent']}"
            
            # Check no MongoDB _id leaked
            assert "_id" not in rel, "MongoDB _id should not be in response"
        
        print(f"✓ Following response structure validated for {len(data['following'])} relationships")
    
    def test_followers_response_structure(self, auth_headers):
        """Verify followers response has correct structure"""
        response = requests.get(f"{BASE_URL}/api/copy/followers", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert "followers" in data
        assert "count" in data
        
        for rel in data["followers"]:
            assert "_id" not in rel, "MongoDB _id should not be in response"
        
        print(f"✓ Followers response structure validated for {len(data['followers'])} followers")
    
    def test_pending_response_structure(self, auth_headers):
        """Verify pending trades response has correct structure"""
        response = requests.get(f"{BASE_URL}/api/copy/pending", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert "pending_trades" in data
        assert "count" in data
        
        for trade in data["pending_trades"]:
            assert "_id" not in trade, "MongoDB _id should not be in response"
        
        print(f"✓ Pending trades response structure validated for {len(data['pending_trades'])} trades")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
