"""
Tests for src/app.py FastAPI backend endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset in-memory activities state before each test"""
    # Store the original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for intramural and regional tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in friendly matches",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 16,
            "participants": ["lucas@mergington.edu", "noah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in school plays and develop acting skills",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu"]
        },
        "Art Class": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop persuasive speaking and critical thinking skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["alexander@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Mondays, 4:00 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["ethan@mergington.edu", "charlotte@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    yield


@pytest.fixture
def client():
    """Create a TestClient for the API"""
    return TestClient(app)


def test_get_activities(client):
    """Test GET /activities endpoint returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Verify all activities are present
    assert len(data) == 9
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    
    # Verify activity structure
    chess = data["Chess Club"]
    assert chess["description"] == "Learn strategies and compete in chess tournaments"
    assert chess["max_participants"] == 12
    assert len(chess["participants"]) == 2
    assert "michael@mergington.edu" in chess["participants"]


def test_signup_for_activity(client):
    """Test POST /activities/{activity_name}/signup adds a student"""
    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    
    # Verify student was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]


def test_signup_duplicate_student(client):
    """Test POST /activities/{activity_name}/signup rejects duplicate signup"""
    # Try to sign up a student who is already registered
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up for this activity"


def test_signup_nonexistent_activity(client):
    """Test POST /activities/{activity_name}/signup fails for invalid activity"""
    response = client.post("/activities/Nonexistent Club/signup?email=newstudent@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_remove_participant(client):
    """Test DELETE /activities/{activity_name}/participants removes a student"""
    response = client.delete("/activities/Chess Club/participants?email=michael@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Removed michael@mergington.edu from Chess Club"
    
    # Verify student was removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]


def test_remove_nonexistent_participant(client):
    """Test DELETE /activities/{activity_name}/participants fails for missing student"""
    response = client.delete("/activities/Chess Club/participants?email=nonexistent@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Participant not found"


def test_remove_from_nonexistent_activity(client):
    """Test DELETE /activities/{activity_name}/participants fails for invalid activity"""
    response = client.delete("/activities/Nonexistent Club/participants?email=michael@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"