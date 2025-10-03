"""RAID and storage redundancy calculations.

This module handles:
- RAID overhead calculations
- Usable vs raw storage
- Filesystem overhead
- Nx Failover configurations
"""

from typing import Dict, Any


def calculate_raid_overhead(
    raw_storage_gb: float,
    raid_usable_percentage: float,
    filesystem_overhead_percentage: float = 5.0,
) -> Dict[str, float]:
    """
    Calculate usable storage after RAID and filesystem overhead.

    Formula: usable = raw × (raid_percentage / 100) × (1 - filesystem_overhead / 100)

    Args:
        raw_storage_gb: Raw storage capacity in GB
        raid_usable_percentage: RAID usable percentage (e.g., 75 for RAID 5, 50 for RAID 1)
        filesystem_overhead_percentage: Filesystem overhead (default 5%)

    Returns:
        Dict with raw_storage_gb, usable_storage_gb, raid_overhead_gb, filesystem_overhead_gb

    Examples:
        >>> # RAID 5 with 4 drives (75% usable)
        >>> calculate_raid_overhead(10000, 75, 5)
        {'raw_storage_gb': 10000, 'usable_storage_gb': 7125.0, ...}

        >>> # RAID 1 (50% usable)
        >>> calculate_raid_overhead(10000, 50, 5)
        {'raw_storage_gb': 10000, 'usable_storage_gb': 4750.0, ...}
    """
    if raw_storage_gb <= 0:
        raise ValueError("Raw storage must be positive")
    if not 0 < raid_usable_percentage <= 100:
        raise ValueError("RAID usable percentage must be between 0 and 100")
    if not 0 <= filesystem_overhead_percentage < 100:
        raise ValueError("Filesystem overhead must be between 0 and 100")

    # Calculate storage after RAID
    storage_after_raid = raw_storage_gb * (raid_usable_percentage / 100)
    raid_overhead = raw_storage_gb - storage_after_raid

    # Calculate storage after filesystem overhead
    usable_storage = storage_after_raid * (1 - filesystem_overhead_percentage / 100)
    filesystem_overhead = storage_after_raid - usable_storage

    return {
        "raw_storage_gb": round(raw_storage_gb, 2),
        "usable_storage_gb": round(usable_storage, 2),
        "raid_overhead_gb": round(raid_overhead, 2),
        "filesystem_overhead_gb": round(filesystem_overhead, 2),
        "raid_usable_percentage": raid_usable_percentage,
        "total_overhead_percentage": round(
            ((raw_storage_gb - usable_storage) / raw_storage_gb) * 100, 2
        ),
    }


def calculate_usable_storage(
    required_storage_gb: float,
    raid_usable_percentage: float,
    filesystem_overhead_percentage: float = 5.0,
) -> Dict[str, float]:
    """
    Calculate raw storage needed to achieve required usable storage.

    This is the inverse of calculate_raid_overhead.

    Args:
        required_storage_gb: Required usable storage in GB
        raid_usable_percentage: RAID usable percentage
        filesystem_overhead_percentage: Filesystem overhead (default 5%)

    Returns:
        Dict with required_storage_gb, raw_storage_needed_gb, overhead details

    Examples:
        >>> # Need 7125 GB usable with RAID 5
        >>> calculate_usable_storage(7125, 75, 5)
        {'required_storage_gb': 7125, 'raw_storage_needed_gb': 10000.0, ...}
    """
    if required_storage_gb <= 0:
        raise ValueError("Required storage must be positive")

    # Calculate raw storage needed
    # usable = raw × (raid% / 100) × (1 - fs% / 100)
    # raw = usable / ((raid% / 100) × (1 - fs% / 100))
    multiplier = (raid_usable_percentage / 100) * (1 - filesystem_overhead_percentage / 100)
    raw_storage_needed = required_storage_gb / multiplier

    # Get full breakdown
    breakdown = calculate_raid_overhead(
        raw_storage_needed, raid_usable_percentage, filesystem_overhead_percentage
    )

    return {
        "required_storage_gb": round(required_storage_gb, 2),
        "raw_storage_needed_gb": round(raw_storage_needed, 2),
        **breakdown,
    }


def calculate_raid_for_drive_count(
    num_drives: int,
    drive_capacity_gb: float,
    raid_type: str,
) -> Dict[str, Any]:
    """
    Calculate RAID configuration for specific drive count.

    Args:
        num_drives: Number of drives
        drive_capacity_gb: Capacity per drive in GB
        raid_type: RAID type ID

    Returns:
        Dict with configuration details

    Raises:
        ValueError: If configuration is invalid
    """
    from app.core.config import ConfigLoader

    raid_config = ConfigLoader.get_raid_by_id(raid_type)

    # Validate minimum drives
    if num_drives < raid_config["min_drives"]:
        raise ValueError(
            f"{raid_config['name']} requires at least {raid_config['min_drives']} drives"
        )

    # Calculate raw storage
    raw_storage = num_drives * drive_capacity_gb

    # Calculate usable storage
    overhead_calc = calculate_raid_overhead(raw_storage, raid_config["usable_percentage"])

    return {
        "raid_type": raid_config["name"],
        "num_drives": num_drives,
        "drive_capacity_gb": drive_capacity_gb,
        "fault_tolerance": raid_config["fault_tolerance"],
        **overhead_calc,
    }


def recommend_raid_type(
    required_storage_gb: float,
    fault_tolerance_required: int = 1,
    performance_priority: str = "balanced",
) -> str:
    """
    Recommend RAID type based on requirements.

    Args:
        required_storage_gb: Required usable storage
        fault_tolerance_required: Number of drive failures to survive (0, 1, or 2)
        performance_priority: "capacity", "performance", or "balanced"

    Returns:
        Recommended RAID type ID

    Examples:
        >>> recommend_raid_type(10000, 1, "balanced")
        'raid5'

        >>> recommend_raid_type(10000, 2, "balanced")
        'raid6'

        >>> recommend_raid_type(10000, 1, "performance")
        'raid10'
    """
    if fault_tolerance_required == 0:
        return "raid0" if performance_priority == "performance" else "none"
    elif fault_tolerance_required == 1:
        if performance_priority == "performance":
            return "raid10"
        elif performance_priority == "capacity":
            return "raid5"
        else:  # balanced
            return "raid5"
    elif fault_tolerance_required >= 2:
        return "raid6"
    else:
        raise ValueError("Invalid fault tolerance requirement")


def calculate_nx_failover_storage(
    primary_storage_gb: float,
    failover_type: str = "n_plus_1",
) -> Dict[str, float]:
    """
    Calculate storage requirements for Nx Failover configuration.

    Args:
        primary_storage_gb: Primary server storage requirement
        failover_type: "none", "n_plus_1", or "n_plus_2"

    Returns:
        Dict with primary, backup, and total storage requirements
    """
    failover_multipliers = {
        "none": 1.0,
        "n_plus_1": 2.0,
        "n_plus_2": 3.0,
    }

    if failover_type not in failover_multipliers:
        raise ValueError(f"Invalid failover type: {failover_type}")

    multiplier = failover_multipliers[failover_type]
    total_storage = primary_storage_gb * multiplier
    backup_storage = total_storage - primary_storage_gb

    return {
        "primary_storage_gb": round(primary_storage_gb, 2),
        "backup_storage_gb": round(backup_storage, 2),
        "total_storage_gb": round(total_storage, 2),
        "failover_type": failover_type,
        "multiplier": multiplier,
    }

