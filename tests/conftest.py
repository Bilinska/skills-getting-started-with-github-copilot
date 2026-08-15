"""
Pytest configuration and fixtures for the test suite.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def activities_data():
    """Fixture providing fresh test data for each test."""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 3,
            "participants": ["emma@mergington.edu"]
        },
        "Empty Activity": {
            "description": "An activity with no participants",
            "schedule": "Mondays, 3:00 PM - 4:00 PM",
            "max_participants": 2,
            "participants": []
        }
    }


@pytest.fixture
def client():
    """Fixture providing a TestClient for the FastAPI app."""
    return TestClient(app)
