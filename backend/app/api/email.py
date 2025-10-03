"""Email API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from io import BytesIO

from app.services.email.sender import EmailService
from app.services.pdf.generator import PDFGenerator, REPORTLAB_AVAILABLE
from app.schemas.calculator import CalculationRequest

router = APIRouter()


class EmailTestRequest(BaseModel):
    """Test email request."""

    recipient_email: EmailStr = Field(..., description="Test recipient email")

    class Config:
        json_schema_extra = {
            "example": {
                "recipient_email": "test@example.com"
            }
        }


class EmailReportRequest(BaseModel):
    """Email report request."""

    recipient_email: EmailStr = Field(..., description="Recipient email address")
    recipient_name: str = Field(..., description="Recipient name")
    cc: Optional[List[EmailStr]] = Field(None, description="CC email addresses")
    include_pdf: bool = Field(default=True, description="Include PDF attachment")

    class Config:
        json_schema_extra = {
            "example": {
                "recipient_email": "customer@example.com",
                "recipient_name": "John Doe",
                "cc": ["manager@example.com"],
                "include_pdf": True
            }
        }


class EmailCalculationRequest(BaseModel):
    """Email calculation request with calculation data."""

    calculation: CalculationRequest
    email: EmailReportRequest

    class Config:
        json_schema_extra = {
            "example": {
                "calculation": {
                    "project": {
                        "project_name": "Test Project",
                        "created_by": "John Doe",
                        "creator_email": "john@example.com"
                    },
                    "camera_groups": [
                        {
                            "num_cameras": 100,
                            "resolution_id": "4mp",
                            "fps": 30,
                            "codec_id": "h264",
                            "quality": "medium",
                            "recording_mode": "continuous",
                            "audio_enabled": False,
                            "bitrate_kbps": 4000
                        }
                    ],
                    "retention_days": 30,
                    "server_config": {
                        "raid_type": "raid5",
                        "failover_type": "none",
                        "nic_capacity_mbps": 1000,
                        "nic_count": 1
                    }
                },
                "email": {
                    "recipient_email": "customer@example.com",
                    "recipient_name": "John Doe",
                    "include_pdf": True
                }
            }
        }


class EmailResponse(BaseModel):
    """Email response."""

    success: bool
    message: str
    recipients: Optional[List[str]] = None
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Email sent successfully to 2 recipient(s)",
                "recipients": ["customer@example.com", "sales@networkoptix.com"]
            }
        }


@router.post("/email/test", response_model=EmailResponse)
async def send_test_email(request: EmailTestRequest):
    """
    Send a test email to verify SMTP configuration.

    This endpoint sends a simple test email to verify that the email
    service is configured correctly and can send emails.
    """
    email_service = EmailService()

    result = await email_service.send_test_email(
        recipient_email=request.recipient_email
    )

    if result["success"]:
        return EmailResponse(
            success=True,
            message=result["message"],
            recipients=result.get("recipients", [])
        )
    else:
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Failed to send email")
        )


@router.post("/email/send-report", response_model=EmailResponse)
async def send_calculation_report_email(
    request: EmailCalculationRequest,
    background_tasks: BackgroundTasks
):
    """
    Calculate system requirements and send report via email.

    This endpoint performs the calculation and sends the results
    via email with an optional PDF attachment. The email is sent
    in the background to avoid blocking the response.
    """
    from app.services.calculations import (
        calculate_bitrate,
        estimate_bitrate_from_preset,
        calculate_storage,
        get_recording_factor,
        calculate_usable_storage,
        calculate_server_count,
        apply_failover,
        calculate_total_bandwidth,
        calculate_per_server_bandwidth,
        validate_nic_capacity,
        calculate_licenses,
    )
    from app.core.config import ConfigLoader

    try:
        # Perform calculation (same logic as /calculate endpoint)
        warnings = []
        errors = []

        total_devices = 0
        total_bitrate_kbps = 0.0
        total_storage_gb = 0.0
        camera_bitrates = []

        for group in request.calculation.camera_groups:
            total_devices += group.num_cameras

            if group.bitrate_kbps:
                bitrate = group.bitrate_kbps
            else:
                bitrate = estimate_bitrate_from_preset(
                    resolution_id=group.resolution_id,
                    fps=group.fps,
                    codec_id=group.codec_id,
                    quality=group.quality,
                    audio_enabled=group.audio_enabled,
                )

            group_bitrate = bitrate * group.num_cameras
            total_bitrate_kbps += group_bitrate
            camera_bitrates.extend([bitrate] * group.num_cameras)

            recording_factor = get_recording_factor(group.recording_mode, group.hours_per_day)
            storage = calculate_storage(
                bitrate_kbps=bitrate,
                retention_days=request.calculation.retention_days,
                recording_factor=recording_factor,
                num_cameras=group.num_cameras,
            )
            total_storage_gb += storage

        # Calculate RAID overhead
        raid_config = ConfigLoader.get_raid_by_id(request.calculation.server_config.raid_type)
        storage_calc = calculate_usable_storage(
            required_storage_gb=total_storage_gb,
            raid_usable_percentage=raid_config["usable_percentage"],
        )

        # Calculate servers
        server_calc = calculate_server_count(
            total_devices=total_devices,
            total_bitrate_mbps=total_bitrate_kbps / 1000,
            nic_capacity_mbps=request.calculation.server_config.nic_capacity_mbps,
            nic_count=request.calculation.server_config.nic_count,
        )

        # Apply failover
        failover_calc = apply_failover(
            servers_needed=server_calc["servers_needed"],
            failover_type=request.calculation.server_config.failover_type,
        )

        # Calculate bandwidth
        bandwidth_calc = calculate_total_bandwidth(camera_bitrates)
        per_server_bw = calculate_per_server_bandwidth(
            total_bitrate_mbps=bandwidth_calc["total_bitrate_mbps"],
            num_servers=server_calc["servers_needed"],
        )

        # Validate NIC capacity
        nic_validation = validate_nic_capacity(
            bitrate_per_server_mbps=per_server_bw["per_server_mbps"],
            nic_capacity_mbps=request.calculation.server_config.nic_capacity_mbps,
            nic_count=request.calculation.server_config.nic_count,
        )

        if not nic_validation["valid"]:
            errors.extend(nic_validation["errors"])
        warnings.extend(nic_validation["warnings"])

        # Calculate licenses
        license_calc = calculate_licenses(num_recorded_devices=total_devices)

        # Build calculation data
        calculation_data = {
            'project': request.calculation.project.model_dump(),
            'summary': {
                'total_devices': total_devices,
                'servers_needed': failover_calc["total_servers"],
                'total_storage_tb': round(total_storage_gb / 1024, 2),
                'total_bitrate_mbps': round(total_bitrate_kbps / 1000, 2),
            },
            'storage': storage_calc,
            'servers': failover_calc,
            'bandwidth': bandwidth_calc,
            'licenses': license_calc,
            'camera_groups': [g.model_dump() for g in request.calculation.camera_groups],
            'retention_days': request.calculation.retention_days,
            'warnings': warnings,
            'errors': errors,
        }

        # Generate PDF if requested
        pdf_buffer = None
        if request.email.include_pdf and REPORTLAB_AVAILABLE:
            pdf_generator = PDFGenerator()
            pdf_buffer = pdf_generator.generate_report(calculation_data)

        # Send email in background
        email_service = EmailService()

        async def send_email_task():
            await email_service.send_calculation_report(
                recipient_email=request.email.recipient_email,
                recipient_name=request.email.recipient_name,
                project_name=request.calculation.project.project_name,
                calculation_data=calculation_data,
                pdf_buffer=pdf_buffer,
                cc=request.email.cc,
            )

        background_tasks.add_task(send_email_task)

        return EmailResponse(
            success=True,
            message=f"Email will be sent to {request.email.recipient_email}",
            recipients=[request.email.recipient_email]
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

