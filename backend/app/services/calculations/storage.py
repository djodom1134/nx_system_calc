"""Storage calculation module.

This module calculates storage requirements based on:
- Bitrate
- Retention period
- Recording schedule (continuous, motion, scheduled)
- Number of cameras
"""

from typing import Optional


def calculate_daily_storage(
    bitrate_kbps: float,
    recording_factor: float = 1.0,
) -> float:
    """
    Calculate daily storage requirement for a single camera in GB.

    Formula: daily_storage_gb = (bitrate_kbps × recording_factor × 86400) / (8 × 1024 × 1024)

    Args:
        bitrate_kbps: Camera bitrate in Kbps
        recording_factor: Recording duty cycle (1.0=continuous, 0.3=motion, 0.5=scheduled)

    Returns:
        Daily storage in GB

    Raises:
        ValueError: If parameters are invalid

    Examples:
        >>> # 4000 Kbps continuous recording
        >>> calculate_daily_storage(4000, 1.0)
        42.19

        >>> # 4000 Kbps motion recording (30% duty cycle)
        >>> calculate_daily_storage(4000, 0.3)
        12.66
    """
    if bitrate_kbps <= 0:
        raise ValueError("Bitrate must be positive")
    if not 0 < recording_factor <= 1.0:
        raise ValueError("Recording factor must be between 0 and 1")

    # Convert Kbps to GB per day
    # bitrate_kbps × seconds_per_day / (8 bits/byte × 1024 KB/MB × 1024 MB/GB)
    seconds_per_day = 86400
    bits_to_gb = 8 * 1024 * 1024

    daily_storage_gb = (bitrate_kbps * recording_factor * seconds_per_day) / bits_to_gb

    return round(daily_storage_gb, 2)


def calculate_storage(
    bitrate_kbps: float,
    retention_days: int,
    recording_factor: float = 1.0,
    num_cameras: int = 1,
) -> float:
    """
    Calculate total storage requirement in GB.

    Args:
        bitrate_kbps: Camera bitrate in Kbps
        retention_days: Number of days to retain footage
        recording_factor: Recording duty cycle (1.0=continuous, 0.3=motion, etc.)
        num_cameras: Number of cameras with this configuration

    Returns:
        Total storage required in GB

    Raises:
        ValueError: If parameters are invalid

    Examples:
        >>> # Single camera, 4000 Kbps, 30 days continuous
        >>> calculate_storage(4000, 30, 1.0, 1)
        1265.63

        >>> # 10 cameras, 2000 Kbps, 14 days motion (30%)
        >>> calculate_storage(2000, 14, 0.3, 10)
        887.11
    """
    if retention_days < 1:
        raise ValueError("Retention days must be at least 1")
    if num_cameras < 1:
        raise ValueError("Number of cameras must be at least 1")

    daily_storage = calculate_daily_storage(bitrate_kbps, recording_factor)
    total_storage = daily_storage * retention_days * num_cameras

    return round(total_storage, 2)


def calculate_storage_with_hours(
    bitrate_kbps: float,
    retention_days: int,
    hours_per_day: float,
    num_cameras: int = 1,
) -> float:
    """
    Calculate storage with custom hours per day.

    This is useful for scheduled recording where you know exact hours.

    Args:
        bitrate_kbps: Camera bitrate in Kbps
        retention_days: Number of days to retain footage
        hours_per_day: Hours of recording per day (1-24)
        num_cameras: Number of cameras

    Returns:
        Total storage required in GB

    Raises:
        ValueError: If parameters are invalid
    """
    if not 0 < hours_per_day <= 24:
        raise ValueError("Hours per day must be between 0 and 24")

    recording_factor = hours_per_day / 24.0
    return calculate_storage(bitrate_kbps, retention_days, recording_factor, num_cameras)


def get_recording_factor(recording_mode: str, custom_hours: Optional[float] = None) -> float:
    """
    Get recording factor based on recording mode.

    Args:
        recording_mode: Recording mode ("continuous", "motion", "object", "scheduled")
        custom_hours: Custom hours per day for scheduled mode

    Returns:
        Recording factor (0-1)

    Raises:
        ValueError: If mode is invalid
    """
    recording_factors = {
        "continuous": 1.0,
        "motion": 0.3,  # Typical 30% duty cycle
        "object": 0.2,  # Typical 20% duty cycle
        "scheduled": 0.5,  # Default 50%, can be customized
    }

    if recording_mode not in recording_factors:
        raise ValueError(f"Invalid recording mode: {recording_mode}")

    factor = recording_factors[recording_mode]

    # Override scheduled with custom hours if provided
    if recording_mode == "scheduled" and custom_hours is not None:
        if not 0 < custom_hours <= 24:
            raise ValueError("Custom hours must be between 0 and 24")
        factor = custom_hours / 24.0

    return factor


def calculate_total_storage_multi_camera(
    camera_configs: list,
) -> dict:
    """
    Calculate total storage for multiple camera configurations.

    Args:
        camera_configs: List of camera configuration dicts with:
            - bitrate_kbps: float
            - retention_days: int
            - recording_factor: float
            - num_cameras: int

    Returns:
        Dict with total_storage_gb and per_camera breakdown

    Examples:
        >>> configs = [
        ...     {"bitrate_kbps": 4000, "retention_days": 30, "recording_factor": 1.0, "num_cameras": 50},
        ...     {"bitrate_kbps": 2000, "retention_days": 30, "recording_factor": 0.3, "num_cameras": 100},
        ... ]
        >>> result = calculate_total_storage_multi_camera(configs)
        >>> result["total_storage_gb"]
        82281.25
    """
    total_storage = 0.0
    breakdown = []

    for config in camera_configs:
        storage = calculate_storage(
            bitrate_kbps=config["bitrate_kbps"],
            retention_days=config["retention_days"],
            recording_factor=config.get("recording_factor", 1.0),
            num_cameras=config["num_cameras"],
        )

        total_storage += storage
        breakdown.append(
            {
                "num_cameras": config["num_cameras"],
                "bitrate_kbps": config["bitrate_kbps"],
                "storage_gb": storage,
                "storage_per_camera_gb": round(storage / config["num_cameras"], 2),
            }
        )

    return {
        "total_storage_gb": round(total_storage, 2),
        "breakdown": breakdown,
    }

