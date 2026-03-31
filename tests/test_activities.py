import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    # Arrange: Client is set up via fixture

    # Act: Make GET request to /activities
    response = client.get("/activities")

    # Assert: Check status code and response structure
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # There are 9 activities

    # Check that each activity has required fields
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_signup_successful(client):
    # Arrange: Choose an activity and email
    activity_name = "Chess Club"
    email = "student@example.com"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Check status code and message
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity_name}" in data["message"]

    # Verify email is in participants by getting activities
    get_response = client.get("/activities")
    activities = get_response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate(client):
    # Arrange: Sign up first
    activity_name = "Programming Class"
    email = "duplicate@example.com"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act: Try to sign up again
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Should fail with 400
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_invalid_activity(client):
    # Arrange: Use non-existent activity
    activity_name = "NonExistent Activity"
    email = "test@example.com"

    # Act: Make POST request
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Should return 404
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_signup_missing_email(client):
    # Arrange: Activity name
    activity_name = "Gym Class"

    # Act: Make POST request without email
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert: Should fail with 422 (validation error)
    assert response.status_code == 422


def test_remove_participant_successful(client):
    # Arrange: First sign up
    activity_name = "Basketball Team"
    email = "remove@example.com"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act: Remove the participant
    response = client.delete(f"/activities/{activity_name}/remove_participant", params={"email": email})

    # Assert: Check status and message
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Removed {email} from {activity_name}" in data["message"]

    # Verify email is removed
    get_response = client.get("/activities")
    activities = get_response.json()
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_not_found(client):
    # Arrange: Activity and email not signed up
    activity_name = "Tennis Club"
    email = "notsigned@example.com"

    # Act: Try to remove
    response = client.delete(f"/activities/{activity_name}/remove_participant", params={"email": email})

    # Assert: Should fail with 404
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_remove_invalid_activity(client):
    # Arrange: Non-existent activity
    activity_name = "Invalid Activity"
    email = "test@example.com"

    # Act: Make DELETE request
    response = client.delete(f"/activities/{activity_name}/remove_participant", params={"email": email})

    # Assert: Should return 404
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_signup_empty_email(client):
    # Arrange: Activity and empty email
    activity_name = "Art Studio"
    email = ""

    # Act: Make POST request
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Should succeed (no validation)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity_name}" in data["message"]

    # Verify email is in participants
    get_response = client.get("/activities")
    activities = get_response.json()
    assert email in activities[activity_name]["participants"]