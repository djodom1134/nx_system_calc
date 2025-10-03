"""Project and calculation persistence models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base


class Project(Base):
    """Project model for storing calculation projects."""
    
    __tablename__ = "projects"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Project details
    project_name = Column(String(255), nullable=False, index=True)
    created_by = Column(String(255), nullable=False)
    creator_email = Column(String(255), nullable=False, index=True)
    receiver_email = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    company_name = Column(String(255), nullable=True)
    
    # Configuration
    retention_days = Column(Integer, nullable=False)
    raid_type = Column(String(50), nullable=False, default="raid5")
    failover_type = Column(String(50), nullable=False, default="none")
    nic_capacity_mbps = Column(Integer, nullable=False, default=1000)
    nic_count = Column(Integer, nullable=False, default=1)
    
    # Calculation results (stored as JSON for flexibility)
    results = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    camera_groups = relationship("CameraGroup", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.project_name}', created_by='{self.created_by}')>"


class CameraGroup(Base):
    """Camera group configuration model."""
    
    __tablename__ = "camera_groups"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Camera configuration
    num_cameras = Column(Integer, nullable=False)
    resolution_id = Column(String(50), nullable=True)
    resolution_area = Column(Integer, nullable=True)
    fps = Column(Integer, nullable=False)
    codec_id = Column(String(50), nullable=False)
    quality = Column(String(50), nullable=False, default="medium")
    bitrate_kbps = Column(Float, nullable=True)
    recording_mode = Column(String(50), nullable=False, default="continuous")
    hours_per_day = Column(Float, nullable=True)
    audio_enabled = Column(Boolean, nullable=False, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="camera_groups")
    
    def __repr__(self):
        return f"<CameraGroup(id={self.id}, project_id={self.project_id}, cameras={self.num_cameras})>"

