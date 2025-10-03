"""Pydantic schemas for calculator API."""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class CameraConfig(BaseModel):
    """Camera configuration input."""

    num_cameras: int = Field(..., ge=1, description="Number of cameras")
    resolution_id: Optional[str] = Field(None, description="Resolution preset ID")
    resolution_area: Optional[int] = Field(None, ge=1, description="Custom resolution area in pixels")
    fps: int = Field(..., ge=1, le=100, description="Frames per second")
    codec_id: str = Field(..., description="Codec ID (h264, h265, mjpeg)")
    quality: str = Field(default="medium", description="Quality level")
    bitrate_kbps: Optional[float] = Field(None, gt=0, description="Manual bitrate override")
    recording_mode: str = Field(default="continuous", description="Recording mode")
    hours_per_day: Optional[float] = Field(None, ge=0, le=24, description="Hours per day for scheduled")
    audio_enabled: bool = Field(default=False, description="Audio recording enabled")

    @field_validator("quality")
    @classmethod
    def validate_quality(cls, v):
        valid = ["low", "medium", "high", "best"]
        if v not in valid:
            raise ValueError(f"Quality must be one of: {valid}")
        return v

    @field_validator("recording_mode")
    @classmethod
    def validate_recording_mode(cls, v):
        valid = ["continuous", "motion", "object", "scheduled"]
        if v not in valid:
            raise ValueError(f"Recording mode must be one of: {valid}")
        return v


class ProjectDetails(BaseModel):
    """Project details."""

    project_name: str = Field(..., min_length=1, description="Project name")
    created_by: str = Field(..., description="Creator name")
    creator_email: str = Field(..., description="Creator email")
    receiver_email: Optional[str] = Field(None, description="Receiver email")
    description: Optional[str] = Field(None, description="Project description")
    company_name: Optional[str] = Field(None, description="Company name for branding")


class ServerConfig(BaseModel):
    """Server configuration."""

    raid_type: str = Field(default="raid5", description="RAID type ID")
    failover_type: str = Field(default="none", description="Failover configuration")
    nic_capacity_mbps: int = Field(default=1000, description="NIC capacity in Mbps")
    nic_count: int = Field(default=1, ge=1, le=4, description="Number of NICs per server")


class CalculationRequest(BaseModel):
    """Complete calculation request."""

    project: ProjectDetails
    camera_groups: List[CameraConfig] = Field(..., min_length=1)
    retention_days: int = Field(..., ge=1, le=365, description="Days of retention")
    server_config: ServerConfig = Field(default_factory=ServerConfig)


class MultiSiteRequest(BaseModel):
    """Multi-site calculation request."""

    project: ProjectDetails
    camera_groups: List[CameraConfig] = Field(..., min_length=1)
    retention_days: int = Field(..., ge=1, le=365, description="Days of retention")
    server_config: ServerConfig = Field(default_factory=ServerConfig)
    max_devices_per_site: int = Field(default=2560, ge=1, description="Maximum devices per site")
    max_servers_per_site: int = Field(default=10, ge=1, description="Maximum servers per site")


class BitrateResult(BaseModel):
    """Bitrate calculation result."""

    bitrate_kbps: float
    bitrate_mbps: float
    video_bitrate_kbps: float
    audio_bitrate_kbps: float


class StorageResult(BaseModel):
    """Storage calculation result."""

    total_storage_gb: float
    total_storage_tb: float
    daily_storage_gb: float
    raw_storage_needed_gb: float
    usable_storage_gb: float
    raid_overhead_gb: float


class ServerResult(BaseModel):
    """Server calculation result."""

    servers_needed: int
    servers_with_failover: int
    devices_per_server: int
    bitrate_per_server_mbps: float
    limiting_factor: str
    recommended_tier: dict


class BandwidthResult(BaseModel):
    """Bandwidth calculation result."""

    total_bitrate_mbps: float
    total_bitrate_gbps: float
    per_server_mbps: float
    nic_utilization_percentage: float


class LicenseResult(BaseModel):
    """License calculation result."""

    professional_licenses: int
    total_licenses: int
    licensing_model: str


class CalculationResponse(BaseModel):
    """Complete calculation response."""

    project: ProjectDetails
    summary: dict
    bitrate: BitrateResult
    storage: StorageResult
    servers: ServerResult
    bandwidth: BandwidthResult
    licenses: LicenseResult
    warnings: List[str] = []
    errors: List[str] = []


class SiteResult(BaseModel):
    """Single site calculation result."""

    site_id: int
    site_name: str
    devices: int
    bitrate_mbps: float
    storage_gb: float
    storage_tb: float
    servers_needed: int
    servers_with_failover: int
    validation: dict


class MultiSiteResponse(BaseModel):
    """Multi-site calculation response."""

    project: ProjectDetails
    sites: List[SiteResult]
    summary: dict
    all_sites_valid: bool
    warnings: List[str] = []
    errors: List[str] = []

