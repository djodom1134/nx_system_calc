"""Tests for project persistence layer."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.project import Project, CameraGroup
from app.services.project_repository import ProjectRepository
from app.schemas.calculator import (
    CalculationRequest,
    ProjectDetails,
    CameraConfig,
    ServerConfig,
)


# Test database setup
@pytest.fixture(scope="function")
def test_db():
    """Create a test database session."""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_calculation_request():
    """Sample calculation request for testing."""
    return CalculationRequest(
        project=ProjectDetails(
            project_name="Test Project",
            created_by="John Doe",
            creator_email="john@example.com",
            receiver_email="receiver@example.com",
            description="Test project description",
            company_name="Test Company",
        ),
        camera_groups=[
            CameraConfig(
                num_cameras=10,
                resolution_id="1080p",
                fps=30,
                codec_id="h265",
                quality="medium",
                recording_mode="continuous",
                audio_enabled=True,
            ),
            CameraConfig(
                num_cameras=5,
                resolution_id="4k",
                fps=15,
                codec_id="h264",
                quality="high",
                recording_mode="motion",
                audio_enabled=False,
            ),
        ],
        retention_days=30,
        server_config=ServerConfig(
            raid_type="raid5",
            failover_type="active_standby",
            nic_capacity_mbps=1000,
            nic_count=2,
        ),
    )


def test_create_project(test_db, sample_calculation_request):
    """Test creating a new project."""
    project = ProjectRepository.create_project(test_db, sample_calculation_request)
    
    assert project.id is not None
    assert project.project_name == "Test Project"
    assert project.created_by == "John Doe"
    assert project.creator_email == "john@example.com"
    assert project.retention_days == 30
    assert project.raid_type == "raid5"
    assert len(project.camera_groups) == 2
    assert project.camera_groups[0].num_cameras == 10
    assert project.camera_groups[1].num_cameras == 5


def test_create_project_with_results(test_db, sample_calculation_request):
    """Test creating a project with calculation results."""
    results = {
        "summary": {
            "total_devices": 15,
            "total_storage_tb": 2.5,
            "servers_needed": 1,
        }
    }
    
    project = ProjectRepository.create_project(test_db, sample_calculation_request, results)
    
    assert project.results is not None
    assert project.results["summary"]["total_devices"] == 15
    assert project.results["summary"]["total_storage_tb"] == 2.5


def test_get_project(test_db, sample_calculation_request):
    """Test retrieving a project by ID."""
    created_project = ProjectRepository.create_project(test_db, sample_calculation_request)
    
    retrieved_project = ProjectRepository.get_project(test_db, created_project.id)
    
    assert retrieved_project is not None
    assert retrieved_project.id == created_project.id
    assert retrieved_project.project_name == "Test Project"
    assert len(retrieved_project.camera_groups) == 2


def test_get_project_not_found(test_db):
    """Test retrieving a non-existent project."""
    project = ProjectRepository.get_project(test_db, 999)
    assert project is None


def test_get_projects(test_db, sample_calculation_request):
    """Test listing projects."""
    # Create multiple projects
    ProjectRepository.create_project(test_db, sample_calculation_request)
    
    request2 = sample_calculation_request.model_copy(deep=True)
    request2.project.project_name = "Test Project 2"
    ProjectRepository.create_project(test_db, request2)
    
    projects = ProjectRepository.get_projects(test_db)
    
    assert len(projects) == 2
    # Should be ordered by created_at descending
    assert projects[0].project_name == "Test Project 2"
    assert projects[1].project_name == "Test Project"


def test_get_projects_with_pagination(test_db, sample_calculation_request):
    """Test listing projects with pagination."""
    # Create 5 projects
    for i in range(5):
        request = sample_calculation_request.model_copy(deep=True)
        request.project.project_name = f"Test Project {i}"
        ProjectRepository.create_project(test_db, request)
    
    # Get first 2
    projects = ProjectRepository.get_projects(test_db, skip=0, limit=2)
    assert len(projects) == 2
    
    # Get next 2
    projects = ProjectRepository.get_projects(test_db, skip=2, limit=2)
    assert len(projects) == 2
    
    # Get last 1
    projects = ProjectRepository.get_projects(test_db, skip=4, limit=2)
    assert len(projects) == 1


def test_get_projects_filter_by_email(test_db, sample_calculation_request):
    """Test filtering projects by creator email."""
    # Create project with first email
    ProjectRepository.create_project(test_db, sample_calculation_request)
    
    # Create project with different email
    request2 = sample_calculation_request.model_copy(deep=True)
    request2.project.creator_email = "other@example.com"
    ProjectRepository.create_project(test_db, request2)
    
    # Filter by first email
    projects = ProjectRepository.get_projects(test_db, creator_email="john@example.com")
    assert len(projects) == 1
    assert projects[0].creator_email == "john@example.com"
    
    # Filter by second email
    projects = ProjectRepository.get_projects(test_db, creator_email="other@example.com")
    assert len(projects) == 1
    assert projects[0].creator_email == "other@example.com"


def test_update_project(test_db, sample_calculation_request):
    """Test updating a project."""
    project = ProjectRepository.create_project(test_db, sample_calculation_request)
    
    # Update the request
    updated_request = sample_calculation_request.model_copy(deep=True)
    updated_request.project.project_name = "Updated Project"
    updated_request.retention_days = 60
    updated_request.camera_groups = [
        CameraConfig(
            num_cameras=20,
            resolution_id="1080p",
            fps=30,
            codec_id="h265",
            quality="high",
            recording_mode="continuous",
            audio_enabled=True,
        )
    ]
    
    updated_project = ProjectRepository.update_project(test_db, project.id, updated_request)
    
    assert updated_project is not None
    assert updated_project.project_name == "Updated Project"
    assert updated_project.retention_days == 60
    assert len(updated_project.camera_groups) == 1
    assert updated_project.camera_groups[0].num_cameras == 20


def test_update_project_with_results(test_db, sample_calculation_request):
    """Test updating a project with new results."""
    project = ProjectRepository.create_project(test_db, sample_calculation_request)
    
    new_results = {
        "summary": {
            "total_devices": 25,
            "total_storage_tb": 5.0,
        }
    }
    
    updated_project = ProjectRepository.update_project(
        test_db, project.id, sample_calculation_request, new_results
    )
    
    assert updated_project.results is not None
    assert updated_project.results["summary"]["total_devices"] == 25


def test_update_project_not_found(test_db, sample_calculation_request):
    """Test updating a non-existent project."""
    updated_project = ProjectRepository.update_project(test_db, 999, sample_calculation_request)
    assert updated_project is None


def test_delete_project(test_db, sample_calculation_request):
    """Test deleting a project."""
    project = ProjectRepository.create_project(test_db, sample_calculation_request)
    
    success = ProjectRepository.delete_project(test_db, project.id)
    assert success is True
    
    # Verify project is deleted
    deleted_project = ProjectRepository.get_project(test_db, project.id)
    assert deleted_project is None


def test_delete_project_not_found(test_db):
    """Test deleting a non-existent project."""
    success = ProjectRepository.delete_project(test_db, 999)
    assert success is False


def test_delete_project_cascades_camera_groups(test_db, sample_calculation_request):
    """Test that deleting a project also deletes camera groups."""
    project = ProjectRepository.create_project(test_db, sample_calculation_request)
    project_id = project.id
    
    # Verify camera groups exist
    camera_groups = test_db.query(CameraGroup).filter(CameraGroup.project_id == project_id).all()
    assert len(camera_groups) == 2
    
    # Delete project
    ProjectRepository.delete_project(test_db, project_id)
    
    # Verify camera groups are deleted
    camera_groups = test_db.query(CameraGroup).filter(CameraGroup.project_id == project_id).all()
    assert len(camera_groups) == 0


def test_project_to_calculation_request(test_db, sample_calculation_request):
    """Test converting a project back to a CalculationRequest."""
    project = ProjectRepository.create_project(test_db, sample_calculation_request)
    
    calc_request = ProjectRepository.project_to_calculation_request(project)
    
    assert calc_request.project.project_name == "Test Project"
    assert calc_request.project.created_by == "John Doe"
    assert calc_request.retention_days == 30
    assert len(calc_request.camera_groups) == 2
    assert calc_request.camera_groups[0].num_cameras == 10
    assert calc_request.server_config.raid_type == "raid5"

