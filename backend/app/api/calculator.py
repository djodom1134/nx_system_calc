"""Calculator API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.schemas.calculator import (
    CalculationRequest,
    CalculationResponse,
    MultiSiteRequest,
    MultiSiteResponse,
)
from app.services.calculations import (
    calculate_bitrate,
    estimate_bitrate_from_preset,
    calculate_storage,
    get_recording_factor,
    calculate_usable_storage,
    calculate_server_count,
    apply_failover,
    recommend_server_tier,
    calculate_total_bandwidth,
    calculate_per_server_bandwidth,
    validate_nic_capacity,
    calculate_licenses,
)
from app.services.calculations.multi_site import calculate_multi_site_deployment
from app.core.config import ConfigLoader, get_settings
from app.services.webhook import WebhookService
from app.schemas.webhook import WebhookEvent

try:
    from app.services.pdf.generator import PDFGenerator
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

router = APIRouter()


@router.post("/calculate", response_model=CalculationResponse)
async def calculate_system(request: CalculationRequest, background_tasks: BackgroundTasks):
    """
    Calculate complete system requirements.

    This endpoint performs all calculations and returns comprehensive results.
    Triggers webhook events if webhooks are enabled.
    """
    try:
        warnings = []
        errors = []

        # Calculate bitrate for each camera group
        total_devices = 0
        total_bitrate_kbps = 0.0
        camera_bitrates = []

        for group in request.camera_groups:
            total_devices += group.num_cameras

            # Calculate or use manual bitrate
            if group.bitrate_kbps:
                bitrate = group.bitrate_kbps
            else:
                if group.resolution_id:
                    bitrate = estimate_bitrate_from_preset(
                        resolution_id=group.resolution_id,
                        fps=group.fps,
                        codec_id=group.codec_id,
                        quality=group.quality,
                        audio_enabled=group.audio_enabled,
                    )
                elif group.resolution_area:
                    codec = ConfigLoader.get_codec_by_id(group.codec_id)
                    quality_mult = codec["quality_multipliers"].get(group.quality, 1.0)
                    bitrate = calculate_bitrate(
                        resolution_area=group.resolution_area,
                        fps=group.fps,
                        compression_factor=codec["compression_factor"],
                        quality_multiplier=quality_mult,
                        audio_enabled=group.audio_enabled,
                    )
                else:
                    raise ValueError("Either resolution_id or resolution_area must be provided")

            # Add to totals
            group_bitrate = bitrate * group.num_cameras
            total_bitrate_kbps += group_bitrate
            camera_bitrates.extend([bitrate] * group.num_cameras)

        # Calculate storage
        total_storage_gb = 0.0
        for group in request.camera_groups:
            # Get bitrate for this group
            if group.bitrate_kbps:
                bitrate = group.bitrate_kbps
            else:
                if group.resolution_id:
                    bitrate = estimate_bitrate_from_preset(
                        group.resolution_id, group.fps, group.codec_id, group.quality, group.audio_enabled
                    )
                else:
                    codec = ConfigLoader.get_codec_by_id(group.codec_id)
                    quality_mult = codec["quality_multipliers"].get(group.quality, 1.0)
                    bitrate = calculate_bitrate(
                        group.resolution_area, group.fps, codec["compression_factor"],
                        quality_mult, group.audio_enabled
                    )

            # Get recording factor
            recording_factor = get_recording_factor(group.recording_mode, group.hours_per_day)

            # Calculate storage for this group
            storage = calculate_storage(
                bitrate_kbps=bitrate,
                retention_days=request.retention_days,
                recording_factor=recording_factor,
                num_cameras=group.num_cameras,
            )
            total_storage_gb += storage

        # Calculate RAID overhead
        raid_config = ConfigLoader.get_raid_by_id(request.server_config.raid_type)
        storage_calc = calculate_usable_storage(
            required_storage_gb=total_storage_gb,
            raid_usable_percentage=raid_config["usable_percentage"],
        )

        # Calculate server count
        total_bitrate_mbps = total_bitrate_kbps / 1000
        server_calc = calculate_server_count(
            total_devices=total_devices,
            total_bitrate_mbps=total_bitrate_mbps,
            nic_capacity_mbps=request.server_config.nic_capacity_mbps,
            nic_count=request.server_config.nic_count,
        )

        # Apply failover
        failover_calc = apply_failover(
            servers_needed=server_calc["servers_needed"],
            failover_type=request.server_config.failover_type,
        )

        # Recommend server tier
        server_tier = recommend_server_tier(
            devices_per_server=server_calc["devices_per_server"],
            bitrate_per_server_mbps=server_calc["bitrate_per_server_mbps"],
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
            nic_capacity_mbps=request.server_config.nic_capacity_mbps,
            nic_count=request.server_config.nic_count,
        )

        if not nic_validation["valid"]:
            errors.extend(nic_validation["errors"])
        warnings.extend(nic_validation["warnings"])

        # Calculate licenses
        license_calc = calculate_licenses(num_recorded_devices=total_devices)

        # Build response
        return CalculationResponse(
            project=request.project,
            summary={
                "total_devices": total_devices,
                "total_storage_tb": round(total_storage_gb / 1024, 2),
                "servers_needed": server_calc["servers_needed"],
                "servers_with_failover": failover_calc["total_servers"],
                "total_bitrate_mbps": round(total_bitrate_mbps, 2),
            },
            bitrate={
                "bitrate_kbps": round(total_bitrate_kbps, 2),
                "bitrate_mbps": round(total_bitrate_mbps, 2),
                "video_bitrate_kbps": round(total_bitrate_kbps, 2),
                "audio_bitrate_kbps": 0.0,
            },
            storage={
                "total_storage_gb": round(total_storage_gb, 2),
                "total_storage_tb": round(total_storage_gb / 1024, 2),
                "daily_storage_gb": round(total_storage_gb / request.retention_days, 2),
                "raw_storage_needed_gb": storage_calc["raw_storage_needed_gb"],
                "usable_storage_gb": storage_calc["usable_storage_gb"],
                "raid_overhead_gb": storage_calc["raid_overhead_gb"],
            },
            servers={
                "servers_needed": server_calc["servers_needed"],
                "servers_with_failover": failover_calc["total_servers"],
                "devices_per_server": server_calc["devices_per_server"],
                "bitrate_per_server_mbps": server_calc["bitrate_per_server_mbps"],
                "limiting_factor": server_calc["limiting_factor"],
                "recommended_tier": server_tier,
            },
            bandwidth={
                "total_bitrate_mbps": bandwidth_calc["total_bitrate_mbps"],
                "total_bitrate_gbps": bandwidth_calc["total_bitrate_gbps"],
                "per_server_mbps": per_server_bw["per_server_mbps"],
                "nic_utilization_percentage": nic_validation["utilization_percentage"],
            },
            licenses={
                "professional_licenses": license_calc["professional_licenses"],
                "total_licenses": license_calc["total_licenses"],
                "licensing_model": "professional",
            },
            warnings=warnings,
            errors=errors,
        )

        # Trigger webhook event if enabled
        settings = get_settings()
        if settings.enable_webhooks:
            webhook_data = {
                "project_name": request.project.project_name,
                "total_devices": total_devices,
                "total_storage_tb": round(total_storage_gb / 1024, 2),
                "servers_needed": server_calc["servers_needed"],
                "total_bitrate_mbps": round(total_bitrate_mbps, 2),
            }
            background_tasks.add_task(
                WebhookService.trigger_event,
                WebhookEvent.CALCULATION_COMPLETED,
                webhook_data
            )

        return response

    except Exception as e:
        # Trigger failure webhook if enabled
        settings = get_settings()
        if settings.enable_webhooks:
            webhook_data = {
                "project_name": request.project.project_name if hasattr(request, 'project') else "Unknown",
                "error": str(e),
            }
            background_tasks.add_task(
                WebhookService.trigger_event,
                WebhookEvent.CALCULATION_FAILED,
                webhook_data
            )
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-pdf")
async def generate_pdf_report(request: CalculationRequest, background_tasks: BackgroundTasks):
    """
    Generate a PDF report for the calculation results.

    This endpoint performs the calculation and returns a PDF report.
    Triggers webhook events if webhooks are enabled.
    """
    if not REPORTLAB_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="PDF generation is not available. ReportLab library is not installed."
        )

    try:
        # Perform the calculation using the same logic as /calculate endpoint
        calc_result = await calculate_system(request, background_tasks)

        # Prepare calculation data for PDF - match the structure expected by PDFGenerator
        calculation_data = {
            'project': {
                'project_name': calc_result.project.project_name,
                'created_by': calc_result.project.created_by,
                'creator_email': calc_result.project.creator_email,
            },
            'summary': calc_result.summary,  # This is already a dict
            'storage': {
                'total_storage_gb': calc_result.storage.total_storage_gb,
                'total_storage_tb': calc_result.storage.total_storage_tb,
                'daily_storage_gb': calc_result.storage.daily_storage_gb,
                'raw_storage_needed_gb': calc_result.storage.raw_storage_needed_gb,
                'usable_storage_gb': calc_result.storage.usable_storage_gb,
                'raid_overhead_gb': calc_result.storage.raid_overhead_gb,
            },
            'servers': {
                'servers_needed': calc_result.servers.servers_needed,
                'servers_with_failover': calc_result.servers.servers_with_failover,
                'devices_per_server': calc_result.servers.devices_per_server,
                'bitrate_per_server_mbps': calc_result.servers.bitrate_per_server_mbps,
                'limiting_factor': calc_result.servers.limiting_factor,
                'recommended_tier': calc_result.servers.recommended_tier,
            },
            'bandwidth': {
                'total_bitrate_mbps': calc_result.bandwidth.total_bitrate_mbps,
                'total_bitrate_gbps': calc_result.bandwidth.total_bitrate_gbps,
                'per_server_mbps': calc_result.bandwidth.per_server_mbps,
                'nic_utilization_percentage': calc_result.bandwidth.nic_utilization_percentage,
            },
            'licenses': {
                'professional_licenses': calc_result.licenses.professional_licenses,
                'total_licenses': calc_result.licenses.total_licenses,
                'licensing_model': calc_result.licenses.licensing_model,
            },
            'retention_days': request.retention_days,
            'warnings': calc_result.warnings,
            'errors': calc_result.errors,
        }

        # Generate PDF
        pdf_generator = PDFGenerator()
        pdf_buffer = pdf_generator.generate_report(calculation_data)

        # Reset buffer position
        pdf_buffer.seek(0)

        # Create filename
        filename = f"{request.project.project_name.replace(' ', '_')}_VMS_Report.pdf"

        # Trigger webhook event for successful PDF generation
        settings = get_settings()
        if settings.enable_webhooks:
            webhook_data = {
                "project_name": request.project.project_name,
                "filename": filename,
                "total_devices": calc_result.summary['total_devices'],
                "total_storage_tb": calc_result.summary['total_storage_tb'],
                "servers_needed": calc_result.servers.servers_needed,
                "pdf_size_bytes": pdf_buffer.getbuffer().nbytes,
            }
            background_tasks.add_task(
                WebhookService.trigger_event,
                WebhookEvent.PDF_GENERATED,
                webhook_data
            )

        # Return PDF as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        # Trigger failure webhook if enabled
        settings = get_settings()
        if settings.enable_webhooks:
            webhook_data = {
                "project_name": request.project.project_name if hasattr(request, 'project') else "Unknown",
                "error": str(e),
            }
            background_tasks.add_task(
                WebhookService.trigger_event,
                WebhookEvent.PDF_FAILED,
                webhook_data
            )
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/calculate/multi-site", response_model=MultiSiteResponse)
async def calculate_multi_site(request: MultiSiteRequest, background_tasks: BackgroundTasks):
    """
    Calculate multi-site deployment requirements.

    This endpoint handles deployments spanning multiple sites with
    automatic distribution of devices across sites based on constraints.
    Triggers webhook events if webhooks are enabled.
    """
    try:
        # Convert camera groups to dict format
        camera_groups = [group.model_dump() for group in request.camera_groups]

        # Convert server config to dict
        server_config = request.server_config.model_dump()

        # Calculate multi-site deployment
        result = calculate_multi_site_deployment(
            camera_groups=camera_groups,
            retention_days=request.retention_days,
            server_config=server_config,
            max_devices_per_site=request.max_devices_per_site,
            max_servers_per_site=request.max_servers_per_site,
        )

        # Collect warnings and errors from site validations
        warnings = []
        errors = []

        for site in result["sites"]:
            validation = site["validation"]
            if validation["warnings"]:
                warnings.extend([f"Site {site['site_id']}: {w}" for w in validation["warnings"]])
            if validation["errors"]:
                errors.extend([f"Site {site['site_id']}: {e}" for e in validation["errors"]])

        response = MultiSiteResponse(
            project=request.project,
            sites=result["sites"],
            summary=result["summary"],
            all_sites_valid=result["all_sites_valid"],
            warnings=warnings,
            errors=errors,
        )

        # Trigger webhook event if enabled
        settings = get_settings()
        if settings.enable_webhooks:
            webhook_data = {
                "project_name": request.project.project_name,
                "total_sites": result["summary"]["total_sites"],
                "total_devices": result["summary"]["total_devices"],
                "total_storage_tb": result["summary"]["total_storage_tb"],
                "total_servers": result["summary"]["total_servers"],
                "all_sites_valid": result["all_sites_valid"],
            }
            background_tasks.add_task(
                WebhookService.trigger_event,
                WebhookEvent.MULTI_SITE_COMPLETED,
                webhook_data
            )

        return response

    except Exception as e:
        # Trigger failure webhook if enabled
        settings = get_settings()
        if settings.enable_webhooks:
            webhook_data = {
                "project_name": request.project.project_name if hasattr(request, 'project') else "Unknown",
                "error": str(e),
            }
            background_tasks.add_task(
                WebhookService.trigger_event,
                WebhookEvent.MULTI_SITE_FAILED,
                webhook_data
            )
        raise HTTPException(status_code=400, detail=str(e))

