"""
Tour Analytics API Tests
Tests for POST /api/analytics/tour and GET /api/analytics/tour/summary endpoints
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestTourAnalyticsPost:
    """Tests for POST /api/analytics/tour endpoint"""
    
    def test_track_step_view_event(self):
        """Track a step_view event with all required fields"""
        session_id = f"test_{uuid.uuid4().hex[:8]}"
        payload = {
            "event_type": "step_view",
            "step_id": "welcome",
            "step_index": 0,
            "session_id": session_id
        }
        response = requests.post(f"{BASE_URL}/api/analytics/tour", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("status") == "tracked", f"Expected status 'tracked', got {data}"
    
    def test_track_step_next_event(self):
        """Track a step_next event"""
        session_id = f"test_{uuid.uuid4().hex[:8]}"
        payload = {
            "event_type": "step_next",
            "step_id": "dashboard",
            "step_index": 1,
            "session_id": session_id
        }
        response = requests.post(f"{BASE_URL}/api/analytics/tour", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "tracked"
    
    def test_track_step_back_event(self):
        """Track a step_back event"""
        session_id = f"test_{uuid.uuid4().hex[:8]}"
        payload = {
            "event_type": "step_back",
            "step_id": "welcome",
            "step_index": 0,
            "session_id": session_id
        }
        response = requests.post(f"{BASE_URL}/api/analytics/tour", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "tracked"
    
    def test_track_skip_event(self):
        """Track a skip event"""
        session_id = f"test_{uuid.uuid4().hex[:8]}"
        payload = {
            "event_type": "skip",
            "step_id": "signals",
            "step_index": 2,
            "session_id": session_id
        }
        response = requests.post(f"{BASE_URL}/api/analytics/tour", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "tracked"
    
    def test_track_complete_event(self):
        """Track a complete event"""
        session_id = f"test_{uuid.uuid4().hex[:8]}"
        payload = {
            "event_type": "complete",
            "step_id": "cta",
            "step_index": 7,
            "session_id": session_id
        }
        response = requests.post(f"{BASE_URL}/api/analytics/tour", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "tracked"
    
    def test_track_cta_click_event(self):
        """Track a cta_click event"""
        session_id = f"test_{uuid.uuid4().hex[:8]}"
        payload = {
            "event_type": "cta_click",
            "step_id": "cta",
            "step_index": 7,
            "session_id": session_id
        }
        response = requests.post(f"{BASE_URL}/api/analytics/tour", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "tracked"
    
    def test_track_restart_event(self):
        """Track a restart event"""
        session_id = f"test_{uuid.uuid4().hex[:8]}"
        payload = {
            "event_type": "restart",
            "step_id": "welcome",
            "step_index": 0,
            "session_id": session_id
        }
        response = requests.post(f"{BASE_URL}/api/analytics/tour", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "tracked"
    
    def test_track_event_without_session_id(self):
        """Track event without session_id (optional field)"""
        payload = {
            "event_type": "step_view",
            "step_id": "welcome",
            "step_index": 0
        }
        response = requests.post(f"{BASE_URL}/api/analytics/tour", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "tracked"
    
    def test_track_event_missing_required_fields(self):
        """Track event with missing required fields should fail"""
        payload = {
            "event_type": "step_view"
            # Missing step_id and step_index
        }
        response = requests.post(f"{BASE_URL}/api/analytics/tour", json=payload)
        # Should return 422 for validation error
        assert response.status_code == 422, f"Expected 422 for missing fields, got {response.status_code}"


class TestTourAnalyticsSummary:
    """Tests for GET /api/analytics/tour/summary endpoint"""
    
    def test_summary_default_days(self):
        """Get summary with default 30 days"""
        response = requests.get(f"{BASE_URL}/api/analytics/tour/summary")
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields exist
        assert "period_days" in data
        assert "totals" in data
        assert "starts" in data
        assert "completes" in data
        assert "cta_clicks" in data
        assert "completion_rate" in data
        assert "cta_rate" in data
        assert "funnel" in data
        assert "dropoff" in data
        assert "daily" in data
        
        # Verify default period
        assert data["period_days"] == 30
    
    def test_summary_custom_days_7(self):
        """Get summary with 7 days period"""
        response = requests.get(f"{BASE_URL}/api/analytics/tour/summary?days=7")
        assert response.status_code == 200
        data = response.json()
        assert data["period_days"] == 7
    
    def test_summary_custom_days_90(self):
        """Get summary with 90 days period"""
        response = requests.get(f"{BASE_URL}/api/analytics/tour/summary?days=90")
        assert response.status_code == 200
        data = response.json()
        assert data["period_days"] == 90
    
    def test_summary_data_types(self):
        """Verify data types in summary response"""
        response = requests.get(f"{BASE_URL}/api/analytics/tour/summary?days=30")
        assert response.status_code == 200
        data = response.json()
        
        # Verify numeric types
        assert isinstance(data["period_days"], int)
        assert isinstance(data["starts"], int)
        assert isinstance(data["completes"], int)
        assert isinstance(data["cta_clicks"], int)
        assert isinstance(data["completion_rate"], (int, float))
        assert isinstance(data["cta_rate"], (int, float))
        
        # Verify list types
        assert isinstance(data["funnel"], list)
        assert isinstance(data["dropoff"], list)
        assert isinstance(data["daily"], list)
        assert isinstance(data["totals"], dict)
    
    def test_summary_funnel_structure(self):
        """Verify funnel data structure"""
        response = requests.get(f"{BASE_URL}/api/analytics/tour/summary?days=30")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["funnel"]) > 0:
            funnel_item = data["funnel"][0]
            assert "step_id" in funnel_item
            assert "step_index" in funnel_item
            assert "views" in funnel_item
            assert "unique_sessions" in funnel_item
    
    def test_summary_dropoff_structure(self):
        """Verify dropoff data structure"""
        response = requests.get(f"{BASE_URL}/api/analytics/tour/summary?days=30")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["dropoff"]) > 0:
            dropoff_item = data["dropoff"][0]
            assert "step_id" in dropoff_item
            assert "step_index" in dropoff_item
            assert "count" in dropoff_item
    
    def test_summary_daily_structure(self):
        """Verify daily data structure"""
        response = requests.get(f"{BASE_URL}/api/analytics/tour/summary?days=30")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["daily"]) > 0:
            daily_item = data["daily"][0]
            assert "date" in daily_item
    
    def test_summary_no_division_by_zero(self):
        """Verify completion_rate and cta_rate handle zero starts gracefully"""
        response = requests.get(f"{BASE_URL}/api/analytics/tour/summary?days=30")
        assert response.status_code == 200
        data = response.json()
        
        # Even if starts is 0, rates should be 0 (not error)
        assert data["completion_rate"] >= 0
        assert data["cta_rate"] >= 0
    
    def test_summary_invalid_days_too_low(self):
        """Test with days < 1 should fail validation"""
        response = requests.get(f"{BASE_URL}/api/analytics/tour/summary?days=0")
        assert response.status_code == 422, f"Expected 422 for days=0, got {response.status_code}"
    
    def test_summary_invalid_days_too_high(self):
        """Test with days > 90 should fail validation"""
        response = requests.get(f"{BASE_URL}/api/analytics/tour/summary?days=100")
        assert response.status_code == 422, f"Expected 422 for days=100, got {response.status_code}"


class TestTourAnalyticsIntegration:
    """Integration tests - track events then verify in summary"""
    
    def test_full_tour_flow_tracking(self):
        """Track a complete tour flow and verify events are counted"""
        session_id = f"integration_test_{uuid.uuid4().hex[:8]}"
        
        # Simulate full tour: step_view for each step, step_next between, complete at end
        steps = ["welcome", "dashboard", "signals", "research", "lab", "agents", "mode", "cta"]
        
        for i, step_id in enumerate(steps):
            # Track step_view
            payload = {
                "event_type": "step_view",
                "step_id": step_id,
                "step_index": i,
                "session_id": session_id
            }
            response = requests.post(f"{BASE_URL}/api/analytics/tour", json=payload)
            assert response.status_code == 200
            
            # Track step_next (except for last step)
            if i < len(steps) - 1:
                payload = {
                    "event_type": "step_next",
                    "step_id": step_id,
                    "step_index": i,
                    "session_id": session_id
                }
                response = requests.post(f"{BASE_URL}/api/analytics/tour", json=payload)
                assert response.status_code == 200
        
        # Track cta_click and complete at the end
        for event_type in ["cta_click", "complete"]:
            payload = {
                "event_type": event_type,
                "step_id": "cta",
                "step_index": 7,
                "session_id": session_id
            }
            response = requests.post(f"{BASE_URL}/api/analytics/tour", json=payload)
            assert response.status_code == 200
        
        # Verify summary reflects the tracked events
        response = requests.get(f"{BASE_URL}/api/analytics/tour/summary?days=1")
        assert response.status_code == 200
        data = response.json()
        
        # Should have at least 1 complete and 1 cta_click
        assert data["completes"] >= 1, f"Expected at least 1 complete, got {data['completes']}"
        assert data["cta_clicks"] >= 1, f"Expected at least 1 cta_click, got {data['cta_clicks']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
