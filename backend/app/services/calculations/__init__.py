"""Calculation services for Nx System Calculator."""

from .bitrate import calculate_bitrate, calculate_bitrate_manual, estimate_bitrate_from_preset
from .storage import calculate_storage, calculate_daily_storage, get_recording_factor
from .raid import calculate_raid_overhead, calculate_usable_storage
from .servers import (
    calculate_server_count,
    calculate_server_distribution,
    apply_failover,
    recommend_server_tier,
)
from .bandwidth import (
    calculate_total_bandwidth,
    calculate_per_server_bandwidth,
    validate_nic_capacity,
)
from .licenses import calculate_licenses

__all__ = [
    "calculate_bitrate",
    "calculate_bitrate_manual",
    "estimate_bitrate_from_preset",
    "calculate_storage",
    "calculate_daily_storage",
    "get_recording_factor",
    "calculate_raid_overhead",
    "calculate_usable_storage",
    "calculate_server_count",
    "calculate_server_distribution",
    "apply_failover",
    "recommend_server_tier",
    "calculate_total_bandwidth",
    "calculate_per_server_bandwidth",
    "validate_nic_capacity",
    "calculate_licenses",
]

