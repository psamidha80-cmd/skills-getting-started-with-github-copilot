import pytest
from fastapi.testclient import TestClient

import src.app as app_module


ACTIVITY_NAME = "Robotics Club"
EXISTING_EMAIL = "existing@mergington.edu"


@pytest.fixture
def client(monkeypatch):
    activities = {
        ACTIVITY_NAME: {
            "description": "Build and program robots",
            "schedule": "Mondays, 3:30 PM",
            "max_participants": 10,
            "participants": [EXISTING_EMAIL],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return TestClient(app_module.app)


def test_get_activities_returns_activity(client):
    # Arrange
    expected_activity = {
        "description": "Build and program robots",
        "schedule": "Mondays, 3:30 PM",
        "max_participants": 10,
        "participants": [EXISTING_EMAIL],
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {ACTIVITY_NAME: expected_activity}


def test_signup_adds_participant(client):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {ACTIVITY_NAME}"}
    participants = client.get("/activities").json()[ACTIVITY_NAME]["participants"]
    assert participants == [EXISTING_EMAIL, email]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = EXISTING_EMAIL

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    participants = client.get("/activities").json()[ACTIVITY_NAME]["participants"]
    assert participants == [EXISTING_EMAIL]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "new@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_unregisters_student(client):
    # Arrange
    email = EXISTING_EMAIL

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {ACTIVITY_NAME}"}
    participants = client.get("/activities").json()[ACTIVITY_NAME]["participants"]
    assert participants == []


def test_remove_participant_rejects_unregistered_student(client):
    # Arrange
    email = "not-signed-up@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    participants = client.get("/activities").json()[ACTIVITY_NAME]["participants"]
    assert participants == [EXISTING_EMAIL]


def test_remove_participant_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": EXISTING_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}