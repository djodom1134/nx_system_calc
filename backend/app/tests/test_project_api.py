"""Integration tests for project API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models.base import Base, get_db


# Test database setup
@pytest.fixture(scope="function", autouse=True)
def test_db():
    """Create a test database."""
    # Create test engine
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    yield

    # Clean up
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "project": {
            "project_name": "API Test Project",
            "created_by": "Jane Doe",
            "creator_email": "jane@example.com",
            "receiver_email": "receiver@example.com",
            "description": "API test description",
            "company_name": "API Test Company",
        },
        "camera_groups": [
            {
                "num_cameras": 15,
                "resolution_id": "1080p",
                "fps": 30,
                "codec_id": "h265",
                "quality": "medium",
                "recording_mode": "continuous",
                "audio_enabled": True,
            }
        ],
        "retention_days": 30,
        "server_config": {
            "raid_type": "raid5",
            "failover_type": "none",
            "nic_capacity_mbps": 1000,
            "nic_count": 1,
        },
    }


def test_create_project_api(client, sample_project_data):
    """Test creating a project via API."""
    response = client.post("/api/v1/projects", json=sample_project_data)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["project_name"] == "API Test Project"
    assert data["created_by"] == "Jane Doe"
    assert data["camera_groups_count"] == 1


def test_list_projects_api(client, sample_project_data):
    """Test listing projects via API."""
    # Create a project first
    client.post("/api/v1/projects", json=sample_project_data)

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["project_name"] == "API Test Project"


def test_list_projects_with_pagination(client, sample_project_data):
    """Test listing projects with pagination."""
    # Create 3 projects
    for i in range(3):
        project_data = sample_project_data.copy()
        project_data["project"]["project_name"] = f"Project {i}"
        client.post("/api/v1/projects", json=project_data)

    # Get first 2
    response = client.get("/api/v1/projects?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Get next 1
    response = client.get("/api/v1/projects?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_list_projects_filter_by_email(client, sample_project_data):
    """Test filtering projects by creator email."""
    # Create project with first email
    client.post("/api/v1/projects", json=sample_project_data)

    # Create project with different email
    project_data2 = sample_project_data.copy()
    project_data2["project"]["creator_email"] = "other@example.com"
    client.post("/api/v1/projects", json=project_data2)

    # Filter by first email
    response = client.get("/api/v1/projects?creator_email=jane@example.com")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["creator_email"] == "jane@example.com"


def test_get_project_api(client, sample_project_data):
    """Test getting a specific project via API."""
    # Create a project
    create_response = client.post("/api/v1/projects", json=sample_project_data)
    project_id = create_response.json()["id"]

    # Get the project
    response = client.get(f"/api/v1/projects/{project_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["project_name"] == "API Test Project"
    assert data["camera_groups_count"] == 1


def test_get_project_not_found(client):
    """Test getting a non-existent project."""
    response = client.get("/api/v1/projects/999")
    assert response.status_code == 404


def test_update_project_api(client, sample_project_data):
    """Test updating a project via API."""
    # Create a project
    create_response = client.post("/api/v1/projects", json=sample_project_data)
    project_id = create_response.json()["id"]

    # Update the project
    updated_data = sample_project_data.copy()
    updated_data["project"]["project_name"] = "Updated API Project"
    updated_data["retention_days"] = 60

    response = client.put(f"/api/v1/projects/{project_id}", json=updated_data)

    assert response.status_code == 200
    data = response.json()
    assert data["project_name"] == "Updated API Project"
    assert data["retention_days"] == 60


def test_update_project_not_found(client, sample_project_data):
    """Test updating a non-existent project."""
    response = client.put("/api/v1/projects/999", json=sample_project_data)
    assert response.status_code == 404


def test_delete_project_api(client, sample_project_data):
    """Test deleting a project via API."""
    # Create a project
    create_response = client.post("/api/v1/projects", json=sample_project_data)
    project_id = create_response.json()["id"]

    # Delete the project
    response = client.delete(f"/api/v1/projects/{project_id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/api/v1/projects/{project_id}")
    assert get_response.status_code == 404


def test_delete_project_not_found(client):
    """Test deleting a non-existent project."""
    response = client.delete("/api/v1/projects/999")
    assert response.status_code == 404


def test_get_project_as_calculation_request(client, sample_project_data):
    """Test getting a project as a CalculationRequest."""
    # Create a project
    create_response = client.post("/api/v1/projects", json=sample_project_data)
    project_id = create_response.json()["id"]

    # Get as calculation request
    response = client.get(f"/api/v1/projects/{project_id}/calculation-request")

    assert response.status_code == 200
    data = response.json()
    assert data["project"]["project_name"] == "API Test Project"
    assert len(data["camera_groups"]) == 1
    assert data["retention_days"] == 30


def test_create_project_with_invalid_data(client):
    """Test creating a project with invalid data."""
    invalid_data = {
        "project": {
            "project_name": "",  # Empty name
            "created_by": "Test",
            "creator_email": "invalid-email",  # Invalid email
        },
        "camera_groups": [],  # Empty camera groups
        "retention_days": -1,  # Invalid retention
    }

    response = client.post("/api/v1/projects", json=invalid_data)
    assert response.status_code == 422  # Validation error


def test_project_timestamps(client, sample_project_data):
    """Test that project timestamps are set correctly."""
    # Create a project
    create_response = client.post("/api/v1/projects", json=sample_project_data)
    data = create_response.json()

    assert "created_at" in data
    assert "updated_at" in data
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_multiple_camera_groups(client, sample_project_data):
    """Test creating a project with multiple camera groups."""
    # Add more camera groups
    sample_project_data["camera_groups"].append({
        "num_cameras": 5,
        "resolution_id": "4k",
        "fps": 15,
        "codec_id": "h264",
        "quality": "high",
        "recording_mode": "motion",
        "audio_enabled": False,
    })

    response = client.post("/api/v1/projects", json=sample_project_data)

    assert response.status_code == 201
    data = response.json()
    assert data["camera_groups_count"] == 2


def test_project_with_results(client, sample_project_data):
    """Test that results field is properly handled."""
    response = client.post("/api/v1/projects", json=sample_project_data)

    assert response.status_code == 201
    data = response.json()
    # Results should be None initially
    assert data["results"] is None or data["results"] == {}

