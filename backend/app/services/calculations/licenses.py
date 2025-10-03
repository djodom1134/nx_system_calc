"""License calculation module.

This module calculates Nx Professional licenses or Nx Evos Services required.
"""

from typing import Dict, Any


def calculate_licenses(
    num_recorded_devices: int,
    num_live_only_devices: int = 0,
    include_io_modules: bool = False,
    num_io_modules: int = 0,
) -> Dict[str, Any]:
    """
    Calculate Nx licenses required.

    Args:
        num_recorded_devices: Number of devices that are recorded
        num_live_only_devices: Number of devices for live viewing only
        include_io_modules: Whether I/O modules are used
        num_io_modules: Number of I/O modules

    Returns:
        Dict with license breakdown

    Examples:
        >>> calculate_licenses(100, 20, False, 0)
        {'professional_licenses': 100, 'live_only_licenses': 20, ...}
    """
    if num_recorded_devices < 0:
        raise ValueError("Number of recorded devices cannot be negative")
    if num_live_only_devices < 0:
        raise ValueError("Number of live-only devices cannot be negative")

    # One professional license per recorded device
    professional_licenses = num_recorded_devices

    # Live-only devices require different licensing
    live_only_licenses = num_live_only_devices

    # I/O modules
    io_licenses = num_io_modules if include_io_modules else 0

    total_licenses = professional_licenses + live_only_licenses + io_licenses

    return {
        "professional_licenses": professional_licenses,
        "live_only_licenses": live_only_licenses,
        "io_module_licenses": io_licenses,
        "total_licenses": total_licenses,
        "breakdown": {
            "recorded_devices": num_recorded_devices,
            "live_only_devices": num_live_only_devices,
            "io_modules": num_io_modules,
        },
    }


def calculate_evos_services(
    num_devices: int,
    service_tier: str = "standard",
) -> Dict[str, Any]:
    """
    Calculate Nx Evos Services required.

    Args:
        num_devices: Total number of devices
        service_tier: Service tier ("basic", "standard", "premium")

    Returns:
        Dict with service requirements

    Examples:
        >>> calculate_evos_services(100, "standard")
        {'num_devices': 100, 'service_tier': 'standard', ...}
    """
    valid_tiers = ["basic", "standard", "premium"]
    if service_tier not in valid_tiers:
        raise ValueError(f"Invalid service tier. Must be one of: {valid_tiers}")

    # Pricing tiers (example - adjust based on actual Nx pricing)
    tier_pricing = {
        "basic": {"monthly_per_device": 5.0, "features": ["Cloud storage", "Basic analytics"]},
        "standard": {
            "monthly_per_device": 10.0,
            "features": ["Cloud storage", "Advanced analytics", "Mobile access"],
        },
        "premium": {
            "monthly_per_device": 20.0,
            "features": [
                "Cloud storage",
                "Advanced analytics",
                "Mobile access",
                "AI features",
                "Priority support",
            ],
        },
    }

    tier_info = tier_pricing[service_tier]
    monthly_cost = num_devices * tier_info["monthly_per_device"]
    annual_cost = monthly_cost * 12

    return {
        "num_devices": num_devices,
        "service_tier": service_tier,
        "monthly_cost_usd": round(monthly_cost, 2),
        "annual_cost_usd": round(annual_cost, 2),
        "cost_per_device_monthly": tier_info["monthly_per_device"],
        "features": tier_info["features"],
    }


def calculate_license_summary(
    camera_groups: list,
    licensing_model: str = "professional",
) -> Dict[str, Any]:
    """
    Calculate comprehensive license summary for multiple camera groups.

    Args:
        camera_groups: List of camera group dicts with num_cameras and recording status
        licensing_model: "professional" or "evos"

    Returns:
        Dict with complete license summary

    Examples:
        >>> groups = [
        ...     {"num_cameras": 100, "recorded": True},
        ...     {"num_cameras": 50, "recorded": False},
        ... ]
        >>> calculate_license_summary(groups, "professional")
        {'total_devices': 150, 'recorded_devices': 100, ...}
    """
    total_devices = sum(group["num_cameras"] for group in camera_groups)
    recorded_devices = sum(
        group["num_cameras"] for group in camera_groups if group.get("recorded", True)
    )
    live_only_devices = total_devices - recorded_devices

    if licensing_model == "professional":
        licenses = calculate_licenses(recorded_devices, live_only_devices)
        return {
            "licensing_model": "professional",
            "total_devices": total_devices,
            "recorded_devices": recorded_devices,
            "live_only_devices": live_only_devices,
            **licenses,
        }
    elif licensing_model == "evos":
        services = calculate_evos_services(total_devices, "standard")
        return {
            "licensing_model": "evos",
            "total_devices": total_devices,
            **services,
        }
    else:
        raise ValueError(f"Invalid licensing model: {licensing_model}")

