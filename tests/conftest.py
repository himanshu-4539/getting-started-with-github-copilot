"""
Pytest configuration and fixtures for the FastAPI application tests.
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    # Store the initial state
    initial_activities = {
        "Basketball": {
            "description": "Team basketball games and practice sessions",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis": {
            "description": "Tennis lessons and competitive matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["lucas@mergington.edu"]
        },
        "Art Club": {
            "description": "Painting, drawing, and other visual arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(initial_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(initial_activities)
