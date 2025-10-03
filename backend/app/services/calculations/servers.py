"""Server count and load distribution calculations.

This module calculates:
- Number of servers needed
- Load distribution across servers
- Server specifications
- Failover configurations

Formulas from core_calculations.md:
- RAM: requiredRAM = ramOS + (hostClient ? clientRam : 0) + cameras × cameraRam
- Storage throughput: storageCount = Math.ceil(bitrate / (1024 × 204))
- NIC count: requiredNICs = Math.ceil((maxBitrate + clientBitrate) / nicBitrate)
"""

import math
from typing import Dict, List, Any, Optional

from app.core.config import ConfigLoader


def calculate_required_ram(
    num_cameras: int,
    cpu_variant: str = "core_i5",
    host_client: bool = False,
    camera_ram_mb: int = 40,
    client_ram_mb: int = 3072,
) -> Dict[str, Any]:
    """
    Calculate required RAM for server.

    Formula from core_calculations.md:
        requiredRAM = ramOS + (hostClient ? clientRam : 0) + cameras × cameraRam

    Constants:
        - camera_ram_mb = 40MB per camera
        - client_ram_mb = 3072MB for desktop client
        - ramOS = 128MB (ARM) or 1024MB (Atom/i3/i5)

    Memory sizing: Rounded to next power of 2, max 64GB

    Args:
        num_cameras: Number of cameras
        cpu_variant: CPU variant ("arm", "atom", "core_i3", "core_i5")
        host_client: Whether server hosts desktop client
        camera_ram_mb: RAM per camera in MB (default 40)
        client_ram_mb: RAM for client in MB (default 3072)

    Returns:
        Dict with required_ram_mb, rounded_ram_gb, and breakdown

    Examples:
        >>> calculate_required_ram(100, "core_i5", False)
        {'required_ram_mb': 5024, 'rounded_ram_gb': 8, ...}
    """
    # Get OS RAM based on CPU variant
    ram_os_map = {
        "arm": 128,
        "atom": 1024,
        "core_i3": 1024,
        "core_i5": 1024,
    }
    ram_os_mb = ram_os_map.get(cpu_variant.lower(), 1024)

    # Calculate required RAM
    required_ram_mb = ram_os_mb
    if host_client:
        required_ram_mb += client_ram_mb
    required_ram_mb += num_cameras * camera_ram_mb

    # Round to next power of 2 (in GB), max 64GB
    required_ram_gb = required_ram_mb / 1024
    powers_of_2 = [1, 2, 4, 8, 16, 32, 64]
    rounded_ram_gb = next((p for p in powers_of_2 if p >= required_ram_gb), 64)

    return {
        "required_ram_mb": required_ram_mb,
        "required_ram_gb": round(required_ram_gb, 2),
        "rounded_ram_gb": rounded_ram_gb,
        "breakdown": {
            "os_ram_mb": ram_os_mb,
            "client_ram_mb": client_ram_mb if host_client else 0,
            "camera_ram_mb": num_cameras * camera_ram_mb,
        },
    }


def calculate_storage_throughput_limit(
    total_bitrate_mbps: float,
    storage_throughput_mbps: int = 204,
) -> Dict[str, Any]:
    """
    Calculate storage device count based on throughput limit.

    Formula from core_calculations.md:
        storageCount = Math.ceil(bitrate / (1024 × 204))

    The constant 204 Mbit/s represents throughput per storage device.

    Args:
        total_bitrate_mbps: Total bitrate in Mbps
        storage_throughput_mbps: Throughput per storage device (default 204)

    Returns:
        Dict with storage_count and throughput info

    Examples:
        >>> calculate_storage_throughput_limit(500)
        {'storage_count': 3, 'throughput_per_device_mbps': 204, ...}
    """
    # Convert to proper units and calculate
    storage_count = math.ceil(total_bitrate_mbps / storage_throughput_mbps)

    return {
        "storage_count": max(1, storage_count),
        "throughput_per_device_mbps": storage_throughput_mbps,
        "total_bitrate_mbps": total_bitrate_mbps,
        "utilization_percentage": round((total_bitrate_mbps / (storage_count * storage_throughput_mbps)) * 100, 1),
    }


def calculate_effective_max_devices(
    resolution_area: int,
    bitrate_kbps: float,
    fps: int,
    base_max_devices: int = 256,
) -> int:
    """
    Calculate effective max devices per server based on camera specs.

    High-bandwidth cameras require fewer devices per server.

    Args:
        resolution_area: Camera resolution in pixels
        bitrate_kbps: Camera bitrate
        fps: Frames per second
        base_max_devices: Base maximum (default 256)

    Returns:
        Effective maximum devices per server
    """
    max_devices = base_max_devices

    # Reduce for high-resolution cameras (≥8MP)
    if resolution_area >= 8000000:
        max_devices = min(max_devices, 128)

    # Reduce for ultra-high resolution (≥12MP)
    if resolution_area >= 12000000:
        max_devices = min(max_devices, 96)

    # Reduce for high bitrate
    if bitrate_kbps > 8000:
        max_devices = min(max_devices, 128)
    if bitrate_kbps > 12000:
        max_devices = min(max_devices, 96)

    # Reduce for high frame rate
    if fps > 30:
        max_devices = int(max_devices * 0.8)

    return max_devices


def calculate_server_count(
    total_devices: int,
    total_bitrate_mbps: float,
    nic_capacity_mbps: float = 1000,
    nic_count: int = 1,
    max_devices_per_server: int = 256,
    bandwidth_headroom: float = 0.2,
    storage_throughput_mbps: int = 204,
    cpu_variant: str = "core_i5",
) -> Dict[str, Any]:
    """
    Calculate number of servers needed.

    Considers device count, bandwidth, storage throughput, and CPU constraints.

    Args:
        total_devices: Total number of cameras
        total_bitrate_mbps: Total bitrate in Mbps
        nic_capacity_mbps: NIC capacity in Mbps (1000 or 10000)
        nic_count: Number of NICs per server
        max_devices_per_server: Maximum devices per server
        bandwidth_headroom: Bandwidth headroom percentage (default 20%)
        storage_throughput_mbps: Storage throughput per device (default 204)
        cpu_variant: CPU variant for camera limits

    Returns:
        Dict with server count and limiting factor

    Examples:
        >>> # 300 devices, 600 Mbps total, 1Gbps NIC
        >>> calculate_server_count(300, 600, 1000, 1, 256, 0.2)
        {'servers_needed': 2, 'limiting_factor': 'device_count', ...}
    """
    if total_devices < 1:
        raise ValueError("Total devices must be at least 1")
    if total_bitrate_mbps < 0:
        raise ValueError("Total bitrate cannot be negative")

    # Get CPU-based camera limit
    from app.core.config import ConfigLoader
    server_specs = ConfigLoader.load_server_specs()
    cpu_variants = server_specs.get("cpu_variants", {})
    cpu_info = cpu_variants.get(cpu_variant, {})
    cpu_max_cameras = cpu_info.get("max_cameras", max_devices_per_server)

    # Calculate servers needed by device count (use CPU limit)
    effective_max_devices = min(max_devices_per_server, cpu_max_cameras)
    servers_by_devices = math.ceil(total_devices / effective_max_devices)

    # Calculate servers needed by bandwidth
    effective_nic_capacity = nic_capacity_mbps * nic_count * (1 - bandwidth_headroom)
    servers_by_bandwidth = math.ceil(total_bitrate_mbps / effective_nic_capacity)

    # Calculate servers needed by storage throughput
    storage_info = calculate_storage_throughput_limit(total_bitrate_mbps, storage_throughput_mbps)
    servers_by_storage = storage_info["storage_count"]

    # Take the maximum of all constraints
    servers_needed = max(servers_by_devices, servers_by_bandwidth, servers_by_storage)

    # Determine limiting factor
    if servers_by_devices >= max(servers_by_bandwidth, servers_by_storage):
        limiting_factor = "device_count"
    elif servers_by_bandwidth >= max(servers_by_devices, servers_by_storage):
        limiting_factor = "bandwidth"
    elif servers_by_storage >= max(servers_by_devices, servers_by_bandwidth):
        limiting_factor = "storage_throughput"
    else:
        limiting_factor = "multiple"

    # Calculate per-server metrics
    devices_per_server = math.ceil(total_devices / servers_needed)
    bitrate_per_server = total_bitrate_mbps / servers_needed

    return {
        "servers_needed": servers_needed,
        "limiting_factor": limiting_factor,
        "servers_by_devices": servers_by_devices,
        "servers_by_bandwidth": servers_by_bandwidth,
        "devices_per_server": devices_per_server,
        "bitrate_per_server_mbps": round(bitrate_per_server, 2),
        "nic_utilization_percentage": round(
            (bitrate_per_server / (nic_capacity_mbps * nic_count)) * 100, 2
        ),
    }


def calculate_failover_capacity(
    max_camera_bitrate_mbps: float,
    cpu_variant: str = "core_i5",
    ram_gb: int = 8,
    nic_bitrate_mbps: float = 600,
    nic_count: int = 1,
    storage_throughput_mbps: int = 204,
    host_client: bool = False,
    camera_ram_mb: int = 40,
    client_ram_mb: int = 3072,
) -> Dict[str, Any]:
    """
    Calculate failover capacity by iteratively adding cameras until resource limits are hit.

    Implements the exact logic from core_calculations.md:
    while (checkRAM() && checkCPU() && checkNIC() && checkHDDCount()) {
        stats.maxBitrate += globalstats.maxCameraBitrate;
        stats.cameras++;
        currentMaxCameras++;
    }

    Args:
        max_camera_bitrate_mbps: Maximum bitrate per camera (peak)
        cpu_variant: CPU variant (arm, atom, core_i3, core_i5)
        ram_gb: Available RAM in GB
        nic_bitrate_mbps: NIC bitrate capacity
        nic_count: Number of NICs
        storage_throughput_mbps: Storage throughput limit (default 204 Mbit/s)
        host_client: Whether server hosts desktop client
        camera_ram_mb: RAM per camera (default 40MB)
        client_ram_mb: RAM for client (default 3072MB)

    Returns:
        Dict with max cameras and resource utilization
    """
    # Get CPU variant specs
    server_specs = ConfigLoader.load_server_specs()
    cpu_variants = server_specs.get("cpu_variants", {})
    cpu_info = cpu_variants.get(cpu_variant, {})
    cpu_max_cameras = cpu_info.get("max_cameras", 256)
    ram_os_mb = cpu_info.get("ram_os_mb", 1024)

    # Available RAM in MB
    available_ram_mb = ram_gb * 1024

    # Total NIC capacity
    total_nic_capacity_mbps = nic_bitrate_mbps * nic_count

    # Initialize counters
    current_cameras = 0
    current_bitrate_mbps = 0.0

    # Iteratively add cameras until hitting a resource limit
    while True:
        # Calculate required resources for next camera
        next_cameras = current_cameras + 1
        next_bitrate_mbps = current_bitrate_mbps + max_camera_bitrate_mbps

        # Check RAM: requiredRAM = ramOS + (hostClient ? clientRam : 0) + cameras × cameraRam
        required_ram_mb = ram_os_mb
        if host_client:
            required_ram_mb += client_ram_mb
        required_ram_mb += next_cameras * camera_ram_mb

        check_ram = available_ram_mb >= required_ram_mb

        # Check CPU: cameras <= cpuVariants[cpu].maxCameras
        check_cpu = next_cameras <= cpu_max_cameras

        # Check NIC: requiredNICs <= nicCount
        required_nics = math.ceil(next_bitrate_mbps / nic_bitrate_mbps)
        check_nic = required_nics <= nic_count

        # Check HDD Count (storage throughput): storageCount = Math.ceil(bitrate / 204)
        required_storage_devices = math.ceil(next_bitrate_mbps / storage_throughput_mbps)
        # Assume we have enough storage devices (this would need actual HDD count from config)
        # For now, we'll use a reasonable limit based on server tier
        max_storage_devices = 12  # Typical max for enterprise servers
        check_hdd = required_storage_devices <= max_storage_devices

        # If all checks pass, add the camera
        if check_ram and check_cpu and check_nic and check_hdd:
            current_cameras = next_cameras
            current_bitrate_mbps = next_bitrate_mbps
        else:
            # Hit a resource limit, stop
            break

    return {
        "max_cameras": current_cameras,
        "max_bitrate_mbps": round(current_bitrate_mbps, 2),
        "ram_utilization_mb": ram_os_mb + (client_ram_mb if host_client else 0) + (current_cameras * camera_ram_mb),
        "ram_utilization_percent": round((ram_os_mb + (client_ram_mb if host_client else 0) + (current_cameras * camera_ram_mb)) / available_ram_mb * 100, 2),
        "cpu_utilization_percent": round(current_cameras / cpu_max_cameras * 100, 2),
        "nic_utilization_percent": round(current_bitrate_mbps / total_nic_capacity_mbps * 100, 2),
        "limiting_factor": _determine_limiting_factor(
            current_cameras, cpu_max_cameras, current_bitrate_mbps,
            total_nic_capacity_mbps, available_ram_mb, ram_os_mb,
            client_ram_mb if host_client else 0, camera_ram_mb
        ),
    }


def _determine_limiting_factor(
    cameras: int, cpu_max: int, bitrate: float, nic_capacity: float,
    ram_available: float, ram_os: float, ram_client: float, ram_per_camera: float
) -> str:
    """Determine which resource is the limiting factor."""
    # Calculate how close we are to each limit
    cpu_usage = cameras / cpu_max if cpu_max > 0 else 0
    nic_usage = bitrate / nic_capacity if nic_capacity > 0 else 0
    ram_usage = (ram_os + ram_client + cameras * ram_per_camera) / ram_available if ram_available > 0 else 0

    # Find the highest usage
    max_usage = max(cpu_usage, nic_usage, ram_usage)

    if max_usage == cpu_usage:
        return "CPU (camera limit)"
    elif max_usage == nic_usage:
        return "Network bandwidth"
    elif max_usage == ram_usage:
        return "RAM"
    else:
        return "Storage throughput"


def apply_failover(
    servers_needed: int,
    failover_type: str = "none",
    cameras_count: int = 0,
    max_camera_bitrate_mbps: float = 0.0,
    cpu_variant: str = "core_i5",
    ram_gb: int = 8,
    nic_bitrate_mbps: float = 600,
    nic_count: int = 1,
) -> Dict[str, Any]:
    """
    Apply failover configuration to server count.

    Uses iterative capacity calculation from core_calculations.md:
    failoverEstimate = Math.max(currentMaxCameras - 1, camerasCount)

    Args:
        servers_needed: Base number of servers
        failover_type: "none", "n_plus_1", or "n_plus_2"
        cameras_count: Total number of cameras
        max_camera_bitrate_mbps: Maximum bitrate per camera
        cpu_variant: CPU variant for capacity calculation
        ram_gb: RAM per server
        nic_bitrate_mbps: NIC bitrate capacity
        nic_count: Number of NICs

    Returns:
        Dict with total servers and failover details
    """
    if failover_type == "none":
        return {
            "primary_servers": servers_needed,
            "backup_servers": 0,
            "total_servers": servers_needed,
            "failover_type": failover_type,
            "failover_capacity": None,
        }

    # Calculate failover capacity if we have camera data
    failover_capacity = None
    if cameras_count > 0 and max_camera_bitrate_mbps > 0:
        capacity_info = calculate_failover_capacity(
            max_camera_bitrate_mbps=max_camera_bitrate_mbps,
            cpu_variant=cpu_variant,
            ram_gb=ram_gb,
            nic_bitrate_mbps=nic_bitrate_mbps,
            nic_count=nic_count,
        )

        # failoverEstimate = Math.max(currentMaxCameras - 1, camerasCount)
        current_max_cameras = capacity_info["max_cameras"]
        failover_estimate = max(current_max_cameras - 1, cameras_count)

        failover_capacity = {
            "max_cameras_per_server": current_max_cameras,
            "failover_estimate": failover_estimate,
            "limiting_factor": capacity_info["limiting_factor"],
            "utilization": {
                "ram_percent": capacity_info["ram_utilization_percent"],
                "cpu_percent": capacity_info["cpu_utilization_percent"],
                "nic_percent": capacity_info["nic_utilization_percent"],
            },
        }

    # For N+1 and N+2, use simple multiplier approach
    # (more sophisticated logic would redistribute cameras across failover servers)
    failover_multipliers = {
        "n_plus_1": 2.0,
        "n_plus_2": 3.0,
    }

    if failover_type not in failover_multipliers:
        raise ValueError(f"Invalid failover type: {failover_type}")

    multiplier = failover_multipliers[failover_type]
    total_servers = int(servers_needed * multiplier)
    backup_servers = total_servers - servers_needed

    return {
        "primary_servers": servers_needed,
        "backup_servers": backup_servers,
        "total_servers": total_servers,
        "failover_type": failover_type,
        "failover_capacity": failover_capacity,
    }


def calculate_server_distribution(
    total_devices: int,
    servers_needed: int,
    camera_configs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Distribute cameras across servers.

    Args:
        total_devices: Total number of cameras
        servers_needed: Number of servers
        camera_configs: List of camera configuration dicts

    Returns:
        List of server configurations with device distribution
    """
    devices_per_server = math.ceil(total_devices / servers_needed)
    servers = []

    remaining_devices = total_devices
    for i in range(servers_needed):
        devices_this_server = min(devices_per_server, remaining_devices)

        servers.append(
            {
                "server_id": i + 1,
                "devices": devices_this_server,
                "utilization_percentage": round((devices_this_server / 256) * 100, 2),
            }
        )

        remaining_devices -= devices_this_server

    return servers


def recommend_server_tier(
    devices_per_server: int,
    bitrate_per_server_mbps: float,
) -> Dict[str, Any]:
    """
    Recommend server tier based on load.

    Args:
        devices_per_server: Number of devices per server
        bitrate_per_server_mbps: Bitrate per server in Mbps

    Returns:
        Recommended server tier configuration
    """
    from app.core.config import ConfigLoader

    server_specs = ConfigLoader.load_server_specs()
    tiers = server_specs["server_tiers"]

    # Find appropriate tier
    recommended_tier = None
    for tier in tiers:
        if (
            devices_per_server <= tier["max_devices"]
            and bitrate_per_server_mbps <= tier["max_bitrate_mbps"]
        ):
            recommended_tier = tier
            break

    # If no tier found, use highest tier
    if recommended_tier is None:
        recommended_tier = tiers[-1]

    # Convert speed_mbps to Gbps for display
    speed_mbps = recommended_tier['network'].get('speed_mbps', recommended_tier['network'].get('speed_gbps', 1000) * 1000)
    speed_gbps = speed_mbps / 1000

    return {
        "recommended_tier": recommended_tier,
        "tier_id": recommended_tier["id"],
        "tier_name": recommended_tier["name"],
        "cpu": recommended_tier["cpu"]["model"],
        "ram_gb": recommended_tier["ram_gb"],
        "storage_type": recommended_tier["storage"]["type"],
        "recommended_raid": recommended_tier["storage"]["recommended_raid"],
        "network": f"{recommended_tier['network']['nics']}x {speed_gbps:.1f}Gbps",
        "use_case": recommended_tier["use_case"],
    }


def validate_site_constraints(
    total_devices: int,
    servers_needed: int,
    max_devices_per_site: int = 2560,
    max_servers_per_site: int = 10,
) -> Dict[str, Any]:
    """
    Validate against site constraints.

    Args:
        total_devices: Total number of devices
        servers_needed: Number of servers needed
        max_devices_per_site: Maximum devices per site (default 2560)
        max_servers_per_site: Maximum servers per site (default 10)

    Returns:
        Dict with validation results and warnings

    Raises:
        ValueError: If constraints are violated
    """
    warnings = []
    errors = []

    if total_devices > max_devices_per_site:
        errors.append(
            f"Total devices ({total_devices}) exceeds maximum per site ({max_devices_per_site}). "
            "Consider splitting into multiple sites."
        )

    if servers_needed > max_servers_per_site:
        errors.append(
            f"Servers needed ({servers_needed}) exceeds maximum per site ({max_servers_per_site}). "
            "Consider splitting into multiple sites or reducing device count."
        )

    if total_devices > max_devices_per_site * 0.9:
        warnings.append(
            f"Approaching maximum devices per site ({total_devices}/{max_devices_per_site})"
        )

    if servers_needed > max_servers_per_site * 0.8:
        warnings.append(
            f"Approaching maximum servers per site ({servers_needed}/{max_servers_per_site})"
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }

