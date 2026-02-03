"""
Tests for the activities endpoints.
"""
import pytest
from fastapi.testclient import TestClient


def test_get_activities(client):
    """Test getting all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Verify structure
    assert isinstance(data, dict)
    assert "Basketball" in data
    assert "Tennis" in data
    assert "Art Club" in data
    
    # Verify activity structure
    basketball = data["Basketball"]
    assert "description" in basketball
    assert "schedule" in basketball
    assert "max_participants" in basketball
    assert "participants" in basketball
    assert isinstance(basketball["participants"], list)


def test_get_activities_contains_initial_participants(client):
    """Test that activities contain initial participants."""
    response = client.get("/activities")
    data = response.json()
    
    assert "alex@mergington.edu" in data["Basketball"]["participants"]
    assert "lucas@mergington.edu" in data["Tennis"]["participants"]
    assert "isabella@mergington.edu" in data["Art Club"]["participants"]


def test_root_redirect(client):
    """Test that root path redirects to static index.html."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_signup_for_activity_success(client):
    """Test successful signup for an activity."""
    response = client.post(
        "/activities/Basketball/signup?email=newemail@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up newemail@mergington.edu for Basketball"
    
    # Verify participant was added
    response = client.get("/activities")
    activities = response.json()
    assert "newemail@mergington.edu" in activities["Basketball"]["participants"]


def test_signup_for_nonexistent_activity(client):
    """Test signup for a non-existent activity."""
    response = client.post(
        "/activities/NonexistentActivity/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_signup_duplicate_email(client):
    """Test signup with an email already registered."""
    response = client.post(
        "/activities/Basketball/signup?email=alex@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up for this activity"


def test_signup_multiple_different_activities(client):
    """Test signing up for multiple different activities."""
    # Sign up first student for two activities
    response1 = client.post(
        "/activities/Basketball/signup?email=student1@mergington.edu"
    )
    assert response1.status_code == 200
    
    response2 = client.post(
        "/activities/Tennis/signup?email=student1@mergington.edu"
    )
    assert response2.status_code == 200
    
    # Verify both signups
    response = client.get("/activities")
    activities = response.json()
    assert "student1@mergington.edu" in activities["Basketball"]["participants"]
    assert "student1@mergington.edu" in activities["Tennis"]["participants"]


def test_unregister_from_activity_success(client):
    """Test successful unregistration from an activity."""
    response = client.delete(
        "/activities/Basketball/unregister?email=alex@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Unregistered alex@mergington.edu from Basketball"
    
    # Verify participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert "alex@mergington.edu" not in activities["Basketball"]["participants"]


def test_unregister_nonexistent_activity(client):
    """Test unregistration from a non-existent activity."""
    response = client.delete(
        "/activities/NonexistentActivity/unregister?email=test@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_unregister_not_signed_up(client):
    """Test unregistration for a student not signed up."""
    response = client.delete(
        "/activities/Basketball/unregister?email=noone@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student is not signed up for this activity"


def test_signup_then_unregister_then_signup_again(client):
    """Test signup, unregister, then signup again."""
    email = "testuser@mergington.edu"
    
    # First signup
    response1 = client.post(f"/activities/Basketball/signup?email={email}")
    assert response1.status_code == 200
    
    # Unregister
    response2 = client.delete(f"/activities/Basketball/unregister?email={email}")
    assert response2.status_code == 200
    
    # Sign up again
    response3 = client.post(f"/activities/Basketball/signup?email={email}")
    assert response3.status_code == 200
    
    # Verify final state
    response = client.get("/activities")
    activities = response.json()
    assert email in activities["Basketball"]["participants"]


def test_activity_capacity(client):
    """Test that activity structure includes capacity information."""
    response = client.get("/activities")
    activities = response.json()
    
    basketball = activities["Basketball"]
    assert basketball["max_participants"] == 15
    assert len(basketball["participants"]) >= 1
    spots_left = basketball["max_participants"] - len(basketball["participants"])
    assert spots_left > 0
