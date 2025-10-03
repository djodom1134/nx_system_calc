"""Project management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.base import get_db
from app.services.project_repository import ProjectRepository
from app.schemas.calculator import CalculationRequest

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectResponse(BaseModel):
    """Project response schema."""
    
    id: int
    project_name: str
    created_by: str
    creator_email: str
    receiver_email: Optional[str]
    description: Optional[str]
    company_name: Optional[str]
    retention_days: int
    raid_type: str
    failover_type: str
    nic_capacity_mbps: int
    nic_count: int
    results: Optional[dict]
    created_at: str
    updated_at: str
    camera_groups_count: int
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Project list item response."""
    
    id: int
    project_name: str
    created_by: str
    creator_email: str
    created_at: str
    updated_at: str
    camera_groups_count: int
    
    class Config:
        from_attributes = True


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(
    request: CalculationRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new project.
    
    This endpoint saves a project configuration to the database.
    The calculation results can be added later via the update endpoint.
    """
    try:
        project = ProjectRepository.create_project(db, request)
        
        return ProjectResponse(
            id=project.id,
            project_name=project.project_name,
            created_by=project.created_by,
            creator_email=project.creator_email,
            receiver_email=project.receiver_email,
            description=project.description,
            company_name=project.company_name,
            retention_days=project.retention_days,
            raid_type=project.raid_type,
            failover_type=project.failover_type,
            nic_capacity_mbps=project.nic_capacity_mbps,
            nic_count=project.nic_count,
            results=project.results,
            created_at=project.created_at.isoformat(),
            updated_at=project.updated_at.isoformat(),
            camera_groups_count=len(project.camera_groups),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[ProjectListResponse])
def list_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    creator_email: Optional[str] = Query(None, description="Filter by creator email"),
    db: Session = Depends(get_db)
):
    """
    List projects with optional filtering.
    
    Returns a paginated list of projects, optionally filtered by creator email.
    """
    projects = ProjectRepository.get_projects(db, skip=skip, limit=limit, creator_email=creator_email)
    
    return [
        ProjectListResponse(
            id=p.id,
            project_name=p.project_name,
            created_by=p.created_by,
            creator_email=p.creator_email,
            created_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat(),
            camera_groups_count=len(p.camera_groups),
        )
        for p in projects
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific project by ID.
    
    Returns the complete project details including camera groups and results.
    """
    project = ProjectRepository.get_project(db, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse(
        id=project.id,
        project_name=project.project_name,
        created_by=project.created_by,
        creator_email=project.creator_email,
        receiver_email=project.receiver_email,
        description=project.description,
        company_name=project.company_name,
        retention_days=project.retention_days,
        raid_type=project.raid_type,
        failover_type=project.failover_type,
        nic_capacity_mbps=project.nic_capacity_mbps,
        nic_count=project.nic_count,
        results=project.results,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat(),
        camera_groups_count=len(project.camera_groups),
    )


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    request: CalculationRequest,
    db: Session = Depends(get_db)
):
    """
    Update an existing project.
    
    Updates the project configuration and camera groups.
    """
    project = ProjectRepository.update_project(db, project_id, request)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse(
        id=project.id,
        project_name=project.project_name,
        created_by=project.created_by,
        creator_email=project.creator_email,
        receiver_email=project.receiver_email,
        description=project.description,
        company_name=project.company_name,
        retention_days=project.retention_days,
        raid_type=project.raid_type,
        failover_type=project.failover_type,
        nic_capacity_mbps=project.nic_capacity_mbps,
        nic_count=project.nic_count,
        results=project.results,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat(),
        camera_groups_count=len(project.camera_groups),
    )


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a project.
    
    Permanently deletes a project and all associated camera groups.
    """
    success = ProjectRepository.delete_project(db, project_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return None


@router.get("/{project_id}/calculation-request", response_model=CalculationRequest)
def get_project_as_calculation_request(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a project as a CalculationRequest.
    
    This endpoint is useful for re-running calculations on a saved project.
    """
    project = ProjectRepository.get_project(db, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectRepository.project_to_calculation_request(project)

