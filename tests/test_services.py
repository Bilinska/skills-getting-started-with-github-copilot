"""
Unit tests for the services module.
Tests individual service functions for correct behavior, validation, and error handling.
"""

import pytest
from fastapi import HTTPException
from copy import deepcopy
from src.services import (
    is_valid_email,
    get_all_activities,
    get_activity,
    signup_participant,
    unregister_participant
)


class TestEmailValidation:
    """Test email validation function."""
    
    def test_valid_email(self):
        """Test that valid emails pass validation."""
        assert is_valid_email("student@mergington.edu") is True
        assert is_valid_email("test@example.com") is True
        assert is_valid_email("a@b.c") is True
    
    def test_invalid_email_no_at_symbol(self):
        """Test that emails without @ symbol fail."""
        assert is_valid_email("invalid.email.com") is False
    
    def test_invalid_email_no_local_part(self):
        """Test that emails with no text before @ fail."""
        assert is_valid_email("@example.com") is False
    
    def test_invalid_email_no_domain(self):
        """Test that emails with no text after @ fail."""
        assert is_valid_email("student@") is False
    
    def test_invalid_email_multiple_at_symbols(self):
        """Test that emails with multiple @ symbols fail."""
        assert is_valid_email("test@@example.com") is False
    
    def test_invalid_email_empty_string(self):
        """Test that empty string fails."""
        assert is_valid_email("") is False
    
    def test_invalid_email_none(self):
        """Test that None fails."""
        assert is_valid_email(None) is False


class TestGetAllActivities:
    """Test get_all_activities function."""
    
    def test_returns_all_activities(self, activities_data):
        """Test that all activities are returned."""
        result = get_all_activities(activities_data)
        assert result == activities_data
        assert len(result) == 3
    
    def test_returns_empty_dict_when_no_activities(self):
        """Test that empty dict is returned when no activities exist."""
        result = get_all_activities({})
        assert result == {}


class TestGetActivity:
    """Test get_activity function."""
    
    def test_returns_activity_when_found(self, activities_data):
        """Test that activity is returned when it exists."""
        result = get_activity(activities_data, "Chess Club")
        assert result["description"] == "Learn strategies and compete in chess tournaments"
        assert result["max_participants"] == 2
    
    def test_raises_404_when_activity_not_found(self, activities_data):
        """Test that 404 is raised when activity doesn't exist."""
        with pytest.raises(HTTPException) as exc_info:
            get_activity(activities_data, "Non-existent Activity")
        assert exc_info.value.status_code == 404
        assert "Activity not found" in exc_info.value.detail


class TestSignupParticipant:
    """Test signup_participant function."""
    
    def test_successful_signup(self, activities_data):
        """Test successful signup for an activity."""
        result = signup_participant(activities_data, "Empty Activity", "new@mergington.edu")
        assert "Signed up" in result
        assert "new@mergington.edu" in activities_data["Empty Activity"]["participants"]
    
    def test_signup_with_invalid_email(self, activities_data):
        """Test that signup fails with invalid email."""
        with pytest.raises(HTTPException) as exc_info:
            signup_participant(activities_data, "Empty Activity", "invalid.email")
        assert exc_info.value.status_code == 400
        assert "Invalid email format" in exc_info.value.detail
    
    def test_signup_for_nonexistent_activity(self, activities_data):
        """Test that signup fails for non-existent activity."""
        with pytest.raises(HTTPException) as exc_info:
            signup_participant(activities_data, "Fake Activity", "student@mergington.edu")
        assert exc_info.value.status_code == 404
        assert "Activity not found" in exc_info.value.detail
    
    def test_signup_duplicate_participant(self, activities_data):
        """Test that duplicate signup is rejected."""
        with pytest.raises(HTTPException) as exc_info:
            signup_participant(activities_data, "Chess Club", "michael@mergington.edu")
        assert exc_info.value.status_code == 409
        assert "already registered" in exc_info.value.detail
    
    def test_signup_when_activity_full(self, activities_data):
        """Test that signup fails when activity is at capacity."""
        # Chess Club has max 2 participants and already has 2
        with pytest.raises(HTTPException) as exc_info:
            signup_participant(activities_data, "Chess Club", "newstudent@mergington.edu")
        assert exc_info.value.status_code == 409
        assert "at capacity" in exc_info.value.detail


class TestUnregisterParticipant:
    """Test unregister_participant function."""
    
    def test_successful_unregister(self, activities_data):
        """Test successful unregister from an activity."""
        result = unregister_participant(activities_data, "Chess Club", "michael@mergington.edu")
        assert "Unregistered" in result
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_with_invalid_email(self, activities_data):
        """Test that unregister fails with invalid email."""
        with pytest.raises(HTTPException) as exc_info:
            unregister_participant(activities_data, "Chess Club", "invalid.email")
        assert exc_info.value.status_code == 400
        assert "Invalid email format" in exc_info.value.detail
    
    def test_unregister_from_nonexistent_activity(self, activities_data):
        """Test that unregister fails for non-existent activity."""
        with pytest.raises(HTTPException) as exc_info:
            unregister_participant(activities_data, "Fake Activity", "student@mergington.edu")
        assert exc_info.value.status_code == 404
        assert "Activity not found" in exc_info.value.detail
    
    def test_unregister_nonexistent_participant(self, activities_data):
        """Test that unregister fails when participant not registered."""
        with pytest.raises(HTTPException) as exc_info:
            unregister_participant(activities_data, "Chess Club", "notregistered@mergington.edu")
        assert exc_info.value.status_code == 404
        assert "not registered" in exc_info.value.detail
