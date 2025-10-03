"""Multi-site calculation module.

This module handles calculations for deployments spanning multiple sites,
with constraints on devices per site and servers per site.
"""

from typing import Dict, List, Any, Optional
import math


def calculate_sites_needed(
    total_devices: int,
    max_devices_per_site: int = 2560,
) -> Dict[str, Any]:
    """
    Calculate number of sites needed based on device count.
    
    Args:
        total_devices: Total number of devices across all sites
        max_devices_per_site: Maximum devices per site (default 2560 = 10 servers × 256 devices)
    
    Returns:
        Dict with sites_needed, devices_per_site breakdown
    
    Examples:
        >>> calculate_sites_needed(1000)
        {'sites_needed': 1, 'devices_per_site': [1000]}
        
        >>> calculate_sites_needed(3000)
        {'sites_needed': 2, 'devices_per_site': [2560, 440]}
    """
    if total_devices < 1:
        raise ValueError("Total devices must be at least 1")
    
    if max_devices_per_site < 1:
        raise ValueError("Max devices per site must be at least 1")
    
    sites_needed = math.ceil(total_devices / max_devices_per_site)
    
    # Distribute devices across sites
    devices_per_site = []
    remaining_devices = total_devices
    
    for i in range(sites_needed):
        if i == sites_needed - 1:
            # Last site gets remaining devices
            devices_per_site.append(remaining_devices)
        else:
            # Fill site to max capacity
            devices_per_site.append(max_devices_per_site)
            remaining_devices -= max_devices_per_site
    
    return {
        "sites_needed": sites_needed,
        "devices_per_site": devices_per_site,
        "max_devices_per_site": max_devices_per_site,
        "total_devices": total_devices,
        "average_devices_per_site": round(total_devices / sites_needed, 1),
    }


def validate_site_configuration(
    devices_per_site: int,
    servers_per_site: int,
    max_devices_per_site: int = 2560,
    max_servers_per_site: int = 10,
    max_devices_per_server: int = 256,
) -> Dict[str, Any]:
    """
    Validate site configuration against constraints.
    
    Args:
        devices_per_site: Number of devices in this site
        servers_per_site: Number of servers in this site
        max_devices_per_site: Maximum devices allowed per site
        max_servers_per_site: Maximum servers allowed per site
        max_devices_per_server: Maximum devices per server
    
    Returns:
        Dict with is_valid, errors, warnings
    """
    errors = []
    warnings = []
    
    # Check device limit
    if devices_per_site > max_devices_per_site:
        errors.append(
            f"Site has {devices_per_site} devices, exceeds maximum of {max_devices_per_site}"
        )
    
    # Check server limit
    if servers_per_site > max_servers_per_site:
        errors.append(
            f"Site has {servers_per_site} servers, exceeds maximum of {max_servers_per_site}"
        )
    
    # Check if servers can handle devices
    max_capacity = servers_per_site * max_devices_per_server
    if devices_per_site > max_capacity:
        errors.append(
            f"Site has {devices_per_site} devices but only {servers_per_site} servers "
            f"(max capacity: {max_capacity} devices)"
        )
    
    # Warnings for approaching limits
    if devices_per_site > max_devices_per_site * 0.9:
        warnings.append(
            f"Site is at {round(devices_per_site / max_devices_per_site * 100)}% capacity"
        )
    
    if servers_per_site > max_servers_per_site * 0.8:
        warnings.append(
            f"Site is using {servers_per_site}/{max_servers_per_site} servers (80%+ utilization)"
        )
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "devices_per_site": devices_per_site,
        "servers_per_site": servers_per_site,
        "utilization_percent": round(devices_per_site / max_devices_per_site * 100, 1),
    }


def calculate_multi_site_deployment(
    camera_groups: List[Dict[str, Any]],
    retention_days: int,
    server_config: Dict[str, Any],
    max_devices_per_site: int = 2560,
    max_servers_per_site: int = 10,
) -> Dict[str, Any]:
    """
    Calculate complete multi-site deployment.
    
    Args:
        camera_groups: List of camera group configurations
        retention_days: Days of retention
        server_config: Server configuration (RAID, failover, NIC)
        max_devices_per_site: Maximum devices per site
        max_servers_per_site: Maximum servers per site
    
    Returns:
        Dict with site-by-site breakdown and aggregate totals
    """
    from app.services.calculations.bitrate import estimate_bitrate_from_preset, calculate_bitrate
    from app.services.calculations.storage import calculate_storage, get_recording_factor
    from app.services.calculations.servers import calculate_server_count, apply_failover
    from app.core.config import ConfigLoader
    
    # Calculate total devices
    total_devices = sum(group["num_cameras"] for group in camera_groups)
    
    # Determine number of sites needed
    sites_info = calculate_sites_needed(total_devices, max_devices_per_site)
    sites_needed = sites_info["sites_needed"]
    
    # Calculate per-site breakdown
    sites = []
    cumulative_devices = 0
    
    for site_idx in range(sites_needed):
        site_devices = sites_info["devices_per_site"][site_idx]
        
        # Distribute camera groups proportionally to this site
        site_camera_groups = []
        site_total_devices = 0
        
        for group in camera_groups:
            # Calculate proportion of this group for this site
            remaining_group_devices = group["num_cameras"] - sum(
                g.get("num_cameras", 0) for s in sites for g in s.get("camera_groups", [])
                if g.get("original_group_id") == id(group)
            )
            
            if remaining_group_devices <= 0:
                continue
            
            # Allocate devices to this site
            devices_for_site = min(
                remaining_group_devices,
                site_devices - site_total_devices
            )
            
            if devices_for_site > 0:
                site_group = group.copy()
                site_group["num_cameras"] = devices_for_site
                site_group["original_group_id"] = id(group)
                site_camera_groups.append(site_group)
                site_total_devices += devices_for_site
        
        # Calculate bitrate for this site
        site_bitrate_kbps = 0.0
        for group in site_camera_groups:
            if group.get("bitrate_kbps"):
                bitrate = group["bitrate_kbps"]
            else:
                if group.get("resolution_id"):
                    bitrate = estimate_bitrate_from_preset(
                        resolution_id=group["resolution_id"],
                        fps=group["fps"],
                        codec_id=group["codec_id"],
                        quality=group.get("quality", "medium"),
                        audio_enabled=group.get("audio_enabled", False),
                    )
                else:
                    codec = ConfigLoader.get_codec_by_id(group["codec_id"])
                    quality_mult = codec["quality_multipliers"].get(group.get("quality", "medium"), 1.0)
                    bitrate = calculate_bitrate(
                        resolution_area=group["resolution_area"],
                        fps=group["fps"],
                        compression_factor=codec["compression_factor"],
                        quality_multiplier=quality_mult,
                        audio_enabled=group.get("audio_enabled", False),
                    )
            
            site_bitrate_kbps += bitrate * group["num_cameras"]
        
        # Calculate storage for this site
        site_storage_gb = 0.0
        for group in site_camera_groups:
            if group.get("bitrate_kbps"):
                bitrate = group["bitrate_kbps"]
            else:
                if group.get("resolution_id"):
                    bitrate = estimate_bitrate_from_preset(
                        group["resolution_id"], group["fps"], group["codec_id"],
                        group.get("quality", "medium"), group.get("audio_enabled", False)
                    )
                else:
                    codec = ConfigLoader.get_codec_by_id(group["codec_id"])
                    quality_mult = codec["quality_multipliers"].get(group.get("quality", "medium"), 1.0)
                    bitrate = calculate_bitrate(
                        group["resolution_area"], group["fps"], codec["compression_factor"],
                        quality_mult, group.get("audio_enabled", False)
                    )
            
            recording_factor = get_recording_factor(
                group.get("recording_mode", "continuous"),
                group.get("hours_per_day")
            )
            
            storage = calculate_storage(
                bitrate_kbps=bitrate,
                retention_days=retention_days,
                recording_factor=recording_factor,
                num_cameras=group["num_cameras"],
            )
            site_storage_gb += storage
        
        # Calculate servers for this site
        server_result = calculate_server_count(
            total_devices=site_total_devices,
            total_bitrate_mbps=site_bitrate_kbps / 1000,
            nic_capacity_mbps=server_config.get("nic_capacity_mbps", 1000),
            nic_count=server_config.get("nic_count", 1),
        )
        
        # Apply failover
        failover_result = apply_failover(
            servers_needed=server_result["servers_needed"],
            failover_type=server_config.get("failover_type", "none"),
        )
        
        # Validate site configuration
        validation = validate_site_configuration(
            devices_per_site=site_total_devices,
            servers_per_site=failover_result["total_servers"],
            max_devices_per_site=max_devices_per_site,
            max_servers_per_site=max_servers_per_site,
        )
        
        sites.append({
            "site_id": site_idx + 1,
            "site_name": f"Site {site_idx + 1}",
            "devices": site_total_devices,
            "camera_groups": site_camera_groups,
            "bitrate_mbps": round(site_bitrate_kbps / 1000, 2),
            "storage_gb": round(site_storage_gb, 2),
            "storage_tb": round(site_storage_gb / 1024, 2),
            "servers_needed": server_result["servers_needed"],
            "servers_with_failover": failover_result["total_servers"],
            "validation": validation,
        })
        
        cumulative_devices += site_total_devices
    
    # Calculate aggregate totals
    total_bitrate_mbps = sum(site["bitrate_mbps"] for site in sites)
    total_storage_tb = sum(site["storage_tb"] for site in sites)
    total_servers = sum(site["servers_with_failover"] for site in sites)
    
    return {
        "sites": sites,
        "summary": {
            "total_sites": sites_needed,
            "total_devices": total_devices,
            "total_bitrate_mbps": round(total_bitrate_mbps, 2),
            "total_storage_tb": round(total_storage_tb, 2),
            "total_servers": total_servers,
            "average_devices_per_site": round(total_devices / sites_needed, 1),
            "max_devices_per_site": max_devices_per_site,
            "max_servers_per_site": max_servers_per_site,
        },
        "all_sites_valid": all(site["validation"]["is_valid"] for site in sites),
    }

