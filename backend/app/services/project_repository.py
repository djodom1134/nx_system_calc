"""Project repository for database operations."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.project import Project, CameraGroup
from app.schemas.calculator import CalculationRequest, ProjectDetails, CameraConfig, ServerConfig


class ProjectRepository:
    """Repository for project CRUD operations."""
    
    @staticmethod
    def create_project(db: Session, request: CalculationRequest, results: dict = None) -> Project:
        """
        Create a new project with camera groups.
        
        Args:
            db: Database session
            request: Calculation request with project details
            results: Optional calculation results to store
            
        Returns:
            Created project instance
        """
        # Create project
        project = Project(
            project_name=request.project.project_name,
            created_by=request.project.created_by,
            creator_email=request.project.creator_email,
            receiver_email=request.project.receiver_email,
            description=request.project.description,
            company_name=request.project.company_name,
            retention_days=request.retention_days,
            raid_type=request.server_config.raid_type,
            failover_type=request.server_config.failover_type,
            nic_capacity_mbps=request.server_config.nic_capacity_mbps,
            nic_count=request.server_config.nic_count,
            results=results,
        )
        
        db.add(project)
        db.flush()  # Get the project ID
        
        # Create camera groups
        for camera_config in request.camera_groups:
            camera_group = CameraGroup(
                project_id=project.id,
                num_cameras=camera_config.num_cameras,
                resolution_id=camera_config.resolution_id,
                resolution_area=camera_config.resolution_area,
                fps=camera_config.fps,
                codec_id=camera_config.codec_id,
                quality=camera_config.quality,
                bitrate_kbps=camera_config.bitrate_kbps,
                recording_mode=camera_config.recording_mode,
                hours_per_day=camera_config.hours_per_day,
                audio_enabled=camera_config.audio_enabled,
            )
            db.add(camera_group)
        
        db.commit()
        db.refresh(project)
        
        return project
    
    @staticmethod
    def get_project(db: Session, project_id: int) -> Optional[Project]:
        """
        Get a project by ID.
        
        Args:
            db: Database session
            project_id: Project ID
            
        Returns:
            Project instance or None if not found
        """
        return db.query(Project).filter(Project.id == project_id).first()
    
    @staticmethod
    def get_projects(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        creator_email: Optional[str] = None
    ) -> List[Project]:
        """
        Get list of projects with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            creator_email: Optional filter by creator email
            
        Returns:
            List of projects
        """
        query = db.query(Project)
        
        if creator_email:
            query = query.filter(Project.creator_email == creator_email)
        
        return query.order_by(desc(Project.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_project(
        db: Session,
        project_id: int,
        request: CalculationRequest,
        results: dict = None
    ) -> Optional[Project]:
        """
        Update an existing project.
        
        Args:
            db: Database session
            project_id: Project ID to update
            request: Updated calculation request
            results: Optional updated calculation results
            
        Returns:
            Updated project instance or None if not found
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            return None
        
        # Update project fields
        project.project_name = request.project.project_name
        project.created_by = request.project.created_by
        project.creator_email = request.project.creator_email
        project.receiver_email = request.project.receiver_email
        project.description = request.project.description
        project.company_name = request.project.company_name
        project.retention_days = request.retention_days
        project.raid_type = request.server_config.raid_type
        project.failover_type = request.server_config.failover_type
        project.nic_capacity_mbps = request.server_config.nic_capacity_mbps
        project.nic_count = request.server_config.nic_count
        
        if results:
            project.results = results
        
        # Delete existing camera groups
        db.query(CameraGroup).filter(CameraGroup.project_id == project_id).delete()
        
        # Create new camera groups
        for camera_config in request.camera_groups:
            camera_group = CameraGroup(
                project_id=project.id,
                num_cameras=camera_config.num_cameras,
                resolution_id=camera_config.resolution_id,
                resolution_area=camera_config.resolution_area,
                fps=camera_config.fps,
                codec_id=camera_config.codec_id,
                quality=camera_config.quality,
                bitrate_kbps=camera_config.bitrate_kbps,
                recording_mode=camera_config.recording_mode,
                hours_per_day=camera_config.hours_per_day,
                audio_enabled=camera_config.audio_enabled,
            )
            db.add(camera_group)
        
        db.commit()
        db.refresh(project)
        
        return project
    
    @staticmethod
    def delete_project(db: Session, project_id: int) -> bool:
        """
        Delete a project.
        
        Args:
            db: Database session
            project_id: Project ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            return False
        
        db.delete(project)
        db.commit()
        
        return True
    
    @staticmethod
    def project_to_calculation_request(project: Project) -> CalculationRequest:
        """
        Convert a project model to a CalculationRequest schema.
        
        Args:
            project: Project model instance
            
        Returns:
            CalculationRequest schema
        """
        return CalculationRequest(
            project=ProjectDetails(
                project_name=project.project_name,
                created_by=project.created_by,
                creator_email=project.creator_email,
                receiver_email=project.receiver_email,
                description=project.description,
                company_name=project.company_name,
            ),
            camera_groups=[
                CameraConfig(
                    num_cameras=cg.num_cameras,
                    resolution_id=cg.resolution_id,
                    resolution_area=cg.resolution_area,
                    fps=cg.fps,
                    codec_id=cg.codec_id,
                    quality=cg.quality,
                    bitrate_kbps=cg.bitrate_kbps,
                    recording_mode=cg.recording_mode,
                    hours_per_day=cg.hours_per_day,
                    audio_enabled=cg.audio_enabled,
                )
                for cg in project.camera_groups
            ],
            retention_days=project.retention_days,
            server_config=ServerConfig(
                raid_type=project.raid_type,
                failover_type=project.failover_type,
                nic_capacity_mbps=project.nic_capacity_mbps,
                nic_count=project.nic_count,
            ),
        )

