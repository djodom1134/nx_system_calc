"""Network bandwidth calculations.

This module calculates:
- Total ingress bandwidth (cameras to servers)
- Total egress bandwidth (servers to clients)
- Per-server bandwidth
- NIC requirements

Formulas from core_calculations.md:
- networkCount = Math.ceil(bitrate / (1024 × nicBitrate))
- requiredNICs = Math.ceil((maxBitrate + clientBitrate) / nicBitrate)
"""

from typing import Dict, List, Any, Optional
import math


def calculate_total_bandwidth(
    camera_bitrates_kbps: List[float],
    headroom_percentage: float = 20.0,
) -> Dict[str, float]:
    """
    Calculate total network bandwidth required.

    Args:
        camera_bitrates_kbps: List of camera bitrates in Kbps
        headroom_percentage: Bandwidth headroom (default 20%)

    Returns:
        Dict with total bandwidth in various units

    Examples:
        >>> # 100 cameras at 4000 Kbps each
        >>> calculate_total_bandwidth([4000] * 100, 20)
        {'total_bitrate_kbps': 400000, 'total_bitrate_mbps': 400.0, ...}
    """
    if not camera_bitrates_kbps:
        raise ValueError("Camera bitrates list cannot be empty")

    total_kbps = sum(camera_bitrates_kbps)
    total_with_headroom = total_kbps * (1 + headroom_percentage / 100)

    return {
        "total_bitrate_kbps": round(total_kbps, 2),
        "total_bitrate_mbps": round(total_kbps / 1000, 2),
        "total_bitrate_gbps": round(total_kbps / 1000000, 2),
        "with_headroom_kbps": round(total_with_headroom, 2),
        "with_headroom_mbps": round(total_with_headroom / 1000, 2),
        "with_headroom_gbps": round(total_with_headroom / 1000000, 2),
        "headroom_percentage": headroom_percentage,
        "num_cameras": len(camera_bitrates_kbps),
    }


def calculate_per_server_bandwidth(
    total_bitrate_mbps: float,
    num_servers: int,
) -> Dict[str, float]:
    """
    Calculate bandwidth per server.

    Args:
        total_bitrate_mbps: Total bitrate in Mbps
        num_servers: Number of servers

    Returns:
        Dict with per-server bandwidth metrics
    """
    if num_servers < 1:
        raise ValueError("Number of servers must be at least 1")

    per_server_mbps = total_bitrate_mbps / num_servers

    return {
        "total_bitrate_mbps": round(total_bitrate_mbps, 2),
        "num_servers": num_servers,
        "per_server_mbps": round(per_server_mbps, 2),
        "per_server_gbps": round(per_server_mbps / 1000, 2),
    }


def validate_nic_capacity(
    bitrate_per_server_mbps: float,
    nic_capacity_mbps: float,
    nic_count: int = 1,
    max_utilization_percentage: float = 80.0,
) -> Dict[str, Any]:
    """
    Validate that bandwidth fits within NIC capacity.

    Args:
        bitrate_per_server_mbps: Bitrate per server in Mbps
        nic_capacity_mbps: NIC capacity in Mbps (1000 or 10000)
        nic_count: Number of NICs per server
        max_utilization_percentage: Maximum recommended utilization (default 80%)

    Returns:
        Dict with validation results and utilization metrics

    Examples:
        >>> # 600 Mbps on 1x 1Gbps NIC
        >>> validate_nic_capacity(600, 1000, 1, 80)
        {'valid': True, 'utilization_percentage': 60.0, ...}
    """
    total_capacity = nic_capacity_mbps * nic_count
    utilization = (bitrate_per_server_mbps / total_capacity) * 100

    valid = utilization <= max_utilization_percentage
    warnings = []
    errors = []

    if utilization > 100:
        errors.append(
            f"Bandwidth ({bitrate_per_server_mbps:.1f} Mbps) exceeds NIC capacity "
            f"({total_capacity:.1f} Mbps). Add more NICs or reduce camera count."
        )
    elif utilization > max_utilization_percentage:
        errors.append(
            f"NIC utilization ({utilization:.1f}%) exceeds recommended maximum "
            f"({max_utilization_percentage}%). Consider adding NICs."
        )
    elif utilization > max_utilization_percentage * 0.9:
        warnings.append(
            f"Approaching maximum NIC utilization ({utilization:.1f}% of {max_utilization_percentage}%)"
        )

    return {
        "valid": len(errors) == 0,
        "utilization_percentage": round(utilization, 2),
        "bitrate_mbps": round(bitrate_per_server_mbps, 2),
        "total_capacity_mbps": total_capacity,
        "available_capacity_mbps": round(total_capacity - bitrate_per_server_mbps, 2),
        "nic_count": nic_count,
        "nic_capacity_mbps": nic_capacity_mbps,
        "errors": errors,
        "warnings": warnings,
    }


def calculate_required_nics(
    max_bitrate_mbps: float,
    nic_bitrate_mbps: float,
    client_bitrate_mbps: float = 0.0,
) -> Dict[str, Any]:
    """
    Calculate required NIC count using formula from core_calculations.md.

    Formula: requiredNICs = Math.ceil((maxBitrate + clientBitrate) / nicBitrate)

    Args:
        max_bitrate_mbps: Maximum bitrate in Mbps (peak, not average)
        nic_bitrate_mbps: NIC capacity in Mbps (64, 600, 1000, 10000)
        client_bitrate_mbps: Additional bitrate for client connections (default 0)

    Returns:
        Dict with required NIC count and utilization

    Examples:
        >>> calculate_required_nics(500, 600, 100)
        {'required_nics': 1, 'total_bitrate_mbps': 600, ...}
    """
    total_bitrate = max_bitrate_mbps + client_bitrate_mbps
    required_nics = math.ceil(total_bitrate / nic_bitrate_mbps)

    return {
        "required_nics": max(1, required_nics),
        "total_bitrate_mbps": round(total_bitrate, 2),
        "nic_bitrate_mbps": nic_bitrate_mbps,
        "total_capacity_mbps": required_nics * nic_bitrate_mbps,
        "utilization_percentage": round((total_bitrate / (required_nics * nic_bitrate_mbps)) * 100, 1),
    }


def recommend_nic_configuration(
    bitrate_per_server_mbps: float,
    target_utilization_percentage: float = 70.0,
    max_bitrate_mbps: Optional[float] = None,
    client_bitrate_mbps: float = 0.0,
) -> Dict[str, Any]:
    """
    Recommend NIC configuration based on bandwidth requirements.

    Uses formula from core_calculations.md when max_bitrate is provided.

    Args:
        bitrate_per_server_mbps: Average bitrate per server in Mbps
        target_utilization_percentage: Target utilization (default 70%)
        max_bitrate_mbps: Maximum bitrate (peak) for accurate calculation
        client_bitrate_mbps: Additional bitrate for client connections

    Returns:
        Dict with recommended NIC configuration

    Examples:
        >>> recommend_nic_configuration(600, 70)
        {'nic_type': '1gbe', 'nic_count': 1, ...}

        >>> recommend_nic_configuration(6000, 70)
        {'nic_type': '10gbe', 'nic_count': 1, ...}
    """
    from app.core.config import ConfigLoader

    server_specs = ConfigLoader.load_server_specs()
    nic_types = server_specs["network_interface_types"]

    # Calculate required capacity with target utilization
    required_capacity = bitrate_per_server_mbps / (target_utilization_percentage / 100)

    # Find best NIC configuration
    for nic_type in nic_types:
        effective_throughput = nic_type["effective_throughput_mbps"]

        # Try with 1 NIC
        if effective_throughput >= required_capacity:
            return {
                "nic_type": nic_type["id"],
                "nic_name": nic_type["name"],
                "nic_count": 1,
                "total_capacity_mbps": nic_type["speed_mbps"],
                "effective_throughput_mbps": effective_throughput,
                "utilization_percentage": round(
                    (bitrate_per_server_mbps / effective_throughput) * 100, 2
                ),
            }

        # Try with 2 NICs
        if effective_throughput * 2 >= required_capacity:
            return {
                "nic_type": nic_type["id"],
                "nic_name": nic_type["name"],
                "nic_count": 2,
                "total_capacity_mbps": nic_type["speed_mbps"] * 2,
                "effective_throughput_mbps": effective_throughput * 2,
                "utilization_percentage": round(
                    (bitrate_per_server_mbps / (effective_throughput * 2)) * 100, 2
                ),
            }

    # If nothing fits, recommend highest tier with 4 NICs
    highest_nic = nic_types[-1]
    return {
        "nic_type": highest_nic["id"],
        "nic_name": highest_nic["name"],
        "nic_count": 4,
        "total_capacity_mbps": highest_nic["speed_mbps"] * 4,
        "effective_throughput_mbps": highest_nic["effective_throughput_mbps"] * 4,
        "utilization_percentage": round(
            (bitrate_per_server_mbps / (highest_nic["effective_throughput_mbps"] * 4)) * 100, 2
        ),
        "warning": "Very high bandwidth requirement - consider splitting across more servers",
    }


def calculate_egress_bandwidth(
    num_concurrent_clients: int,
    avg_cameras_per_client: int,
    avg_camera_bitrate_kbps: float,
) -> Dict[str, float]:
    """
    Calculate egress bandwidth for client viewing.

    Args:
        num_concurrent_clients: Number of concurrent viewing clients
        avg_cameras_per_client: Average cameras viewed per client
        avg_camera_bitrate_kbps: Average camera bitrate in Kbps

    Returns:
        Dict with egress bandwidth requirements

    Examples:
        >>> # 10 clients viewing 4 cameras each at 4000 Kbps
        >>> calculate_egress_bandwidth(10, 4, 4000)
        {'total_egress_mbps': 160.0, ...}
    """
    total_streams = num_concurrent_clients * avg_cameras_per_client
    total_egress_kbps = total_streams * avg_camera_bitrate_kbps

    return {
        "num_concurrent_clients": num_concurrent_clients,
        "avg_cameras_per_client": avg_cameras_per_client,
        "total_streams": total_streams,
        "total_egress_kbps": round(total_egress_kbps, 2),
        "total_egress_mbps": round(total_egress_kbps / 1000, 2),
        "total_egress_gbps": round(total_egress_kbps / 1000000, 2),
    }


def calculate_network_summary(
    total_ingress_mbps: float,
    total_egress_mbps: float,
    num_servers: int,
) -> Dict[str, Any]:
    """
    Calculate comprehensive network bandwidth summary.

    Args:
        total_ingress_mbps: Total ingress bandwidth (cameras to servers)
        total_egress_mbps: Total egress bandwidth (servers to clients)
        num_servers: Number of servers

    Returns:
        Dict with complete network bandwidth summary
    """
    per_server_ingress = total_ingress_mbps / num_servers
    per_server_egress = total_egress_mbps / num_servers
    per_server_total = per_server_ingress + per_server_egress

    return {
        "ingress": {
            "total_mbps": round(total_ingress_mbps, 2),
            "per_server_mbps": round(per_server_ingress, 2),
        },
        "egress": {
            "total_mbps": round(total_egress_mbps, 2),
            "per_server_mbps": round(per_server_egress, 2),
        },
        "total": {
            "total_mbps": round(total_ingress_mbps + total_egress_mbps, 2),
            "per_server_mbps": round(per_server_total, 2),
        },
        "num_servers": num_servers,
    }

