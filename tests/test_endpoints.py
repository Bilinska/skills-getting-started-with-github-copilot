"""
Integration tests for the API endpoints.
Tests the full request/response flow through FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
from copy import deepcopy


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to known state before each test."""
    original = deepcopy(activities)
    
    # Reinitialize activities to a clean state
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,
            "participants": ["michael@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 2,
            "participants": ["emma@mergington.edu"]
        }
    })
    
    yield
    
    # Restore original state after test
    activities.clear()
    activities.update(original)


class TestGetActivitiesEndpoint:
    """Test GET /activities endpoint."""
    
    def test_get_activities_success(self):
        """Test successful retrieval of all activities."""
        client = TestClient(app)
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert data["Chess Club"]["max_participants"] == 2
    
    def test_get_activities_returns_participants(self):
        """Test that activities include participant list."""
        client = TestClient(app)
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        assert "participants" in data["Chess Club"]
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestSignupEndpoint:
    """Test POST /activities/{activity_name}/signup endpoint."""
    
    def test_successful_signup(self):
        """Test successful signup for an activity."""
        client = TestClient(app)
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        
        # Verify participant was added
        check_response = client.get("/activities")
        participants = check_response.json()["Programming Class"]["participants"]
        assert "newstudent@mergington.edu" in participants
    
    def test_signup_with_invalid_email(self):
        """Test signup fails with invalid email format."""
        client = TestClient(app)
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "invalid.email"}
        )
        
        assert response.status_code == 400
        assert "Invalid email format" in response.json()["detail"]
    
    def test_signup_for_nonexistent_activity(self):
        """Test signup fails for non-existent activity."""
        client = TestClient(app)
        response = client.post(
            "/activities/Fake Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_participant(self):
        """Test signup fails for duplicate registration."""
        client = TestClient(app)
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"]
    
    def test_signup_when_activity_full(self):
        """Test signup fails when activity is at capacity."""
        client = TestClient(app)
        
        # First, fill the activity to capacity
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "second@mergington.edu"}
        )
        
        # Now try to add another
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "third@mergington.edu"}
        )
        
        assert response.status_code == 409
        assert "at capacity" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Test DELETE /activities/{activity_name}/signup endpoint."""
    
    def test_successful_unregister(self):
        """Test successful unregister from an activity."""
        client = TestClient(app)
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        check_response = client.get("/activities")
        participants = check_response.json()["Chess Club"]["participants"]
        assert "michael@mergington.edu" not in participants
    
    def test_unregister_with_invalid_email(self):
        """Test unregister fails with invalid email format."""
        client = TestClient(app)
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "invalid.email"}
        )
        
        assert response.status_code == 400
        assert "Invalid email format" in response.json()["detail"]
    
    def test_unregister_from_nonexistent_activity(self):
        """Test unregister fails for non-existent activity."""
        client = TestClient(app)
        response = client.delete(
            "/activities/Fake Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_nonexistent_participant(self):
        """Test unregister fails when participant not registered."""
        client = TestClient(app)
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "notregistered@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_opens_capacity(self):
        """Test that unregistering opens up a spot for signup."""
        client = TestClient(app)
        
        # Add second participant to reach capacity
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "second@mergington.edu"}
        )
        
        # Unregister one participant
        client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        
        # Now we should be able to add another
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "third@mergington.edu"}
        )
        
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
