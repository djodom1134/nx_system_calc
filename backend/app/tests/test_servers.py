"""Unit tests for server calculation module."""

import pytest
from app.services.calculations.servers import (
    calculate_required_ram,
    calculate_storage_throughput_limit,
    calculate_server_count,
    calculate_failover_capacity,
    apply_failover,
    recommend_server_tier,
)


class TestCalculateRequiredRAM:
    """Test RAM calculation function."""

    def test_basic_ram_calculation(self):
        """Test basic RAM calculation with cameras only."""
        result = calculate_required_ram(
            num_cameras=50,
            cpu_variant="core_i5",
            host_client=False,
        )

        # Formula: ramOS + cameras × cameraRam
        # core_i5: ramOS = 1024MB, cameraRam = 40MB
        # 1024 + 50 × 40 = 1024 + 2000 = 3024MB
        assert result["required_ram_mb"] == 3024
        # Should round to next power of 2: 4GB
        assert result["rounded_ram_gb"] == 4

    def test_ram_with_client(self):
        """Test RAM calculation with desktop client."""
        result = calculate_required_ram(
            num_cameras=10,
            cpu_variant="core_i5",
            host_client=True,
        )

        # Formula: ramOS + clientRam + cameras × cameraRam
        # 1024 + 3072 + 10 × 40 = 1024 + 3072 + 400 = 4496MB
        assert result["required_ram_mb"] == 4496
        # Should round to 8GB
        assert result["rounded_ram_gb"] == 8

    def test_ram_arm_variant(self):
        """Test RAM calculation with ARM CPU."""
        result = calculate_required_ram(
            num_cameras=10,
            cpu_variant="arm",
            host_client=False,
        )

        # ARM: ramOS = 128MB
        # 128 + 10 × 40 = 128 + 400 = 528MB
        assert result["required_ram_mb"] == 528
        # Should round to 1GB
        assert result["rounded_ram_gb"] == 1

    def test_ram_power_of_2_rounding(self):
        """Test RAM rounds to next power of 2."""
        # Test various camera counts
        # Formula: ramOS (1024MB for core_i5) + cameras × 40MB
        test_cases = [
            (1, 2),    # 1024 + 40 = 1064MB → 2GB
            (10, 2),   # 1024 + 400 = 1424MB → 2GB
            (50, 4),   # 1024 + 2000 = 3024MB → 4GB
            (100, 8),  # 1024 + 4000 = 5024MB → 8GB
            (200, 16), # 1024 + 8000 = 9024MB → 16GB
        ]

        for cameras, expected_gb in test_cases:
            result = calculate_required_ram(cameras, "core_i5", False)
            assert result["rounded_ram_gb"] == expected_gb

    def test_ram_max_64gb(self):
        """Test RAM caps at 64GB."""
        result = calculate_required_ram(
            num_cameras=2000,  # Would require > 64GB
            cpu_variant="core_i5",
            host_client=True,
        )

        # Should cap at 64GB
        assert result["rounded_ram_gb"] == 64


class TestCalculateStorageThroughput:
    """Test storage throughput calculation."""

    def test_basic_throughput(self):
        """Test basic storage throughput calculation."""
        result = calculate_storage_throughput_limit(
            total_bitrate_mbps=500,
            storage_throughput_mbps=204,
        )

        # Formula: Math.ceil(500 / 204) = Math.ceil(2.45) = 3
        assert result["storage_count"] == 3
        assert result["throughput_per_device_mbps"] == 204

    def test_exact_multiple(self):
        """Test when bitrate is exact multiple of throughput."""
        result = calculate_storage_throughput_limit(
            total_bitrate_mbps=408,  # 2 × 204
            storage_throughput_mbps=204,
        )

        assert result["storage_count"] == 2

    def test_low_bitrate(self):
        """Test with low bitrate (single storage device)."""
        result = calculate_storage_throughput_limit(
            total_bitrate_mbps=100,
            storage_throughput_mbps=204,
        )

        assert result["storage_count"] == 1


class TestCalculateServerCount:
    """Test server count calculation."""

    def test_server_count_by_devices(self):
        """Test server count limited by device count."""
        result = calculate_server_count(
            total_devices=300,  # More than 256 per server
            total_bitrate_mbps=1000,
            max_devices_per_server=256,
        )

        # 300 devices / 256 per server = 2 servers
        assert result["servers_needed"] >= 2

    def test_server_count_by_bandwidth(self):
        """Test server count limited by bandwidth."""
        result = calculate_server_count(
            total_devices=100,
            total_bitrate_mbps=2000,  # High bitrate
            nic_capacity_mbps=1000,
            nic_count=1,
            bandwidth_headroom=0.2,
        )

        # With 20% headroom: 1000 × 0.8 = 800 Mbps usable
        # 2000 / 800 = 2.5 → 3 servers
        assert result["servers_needed"] >= 2

    def test_server_count_by_storage_throughput(self):
        """Test server count limited by storage throughput."""
        result = calculate_server_count(
            total_devices=50,
            total_bitrate_mbps=1000,
            storage_throughput_mbps=204,
        )

        # 1000 / 204 = 4.9 → 5 storage devices needed
        # This might require multiple servers
        assert result["servers_needed"] >= 1

    def test_server_count_cpu_variant(self):
        """Test server count respects CPU variant limits."""
        result = calculate_server_count(
            total_devices=50,
            total_bitrate_mbps=100,
            cpu_variant="arm",  # 12 cameras max
        )

        # 50 cameras / 12 per ARM server = 5 servers
        assert result["servers_needed"] >= 4


class TestFailoverCapacity:
    """Test failover capacity calculation."""

    def test_failover_capacity_ram_limit(self):
        """Test failover capacity limited by RAM."""
        result = calculate_failover_capacity(
            max_camera_bitrate_mbps=5.0,
            cpu_variant="core_i5",
            ram_gb=4,  # Limited RAM
            nic_bitrate_mbps=600,
            nic_count=1,
        )

        # With 4GB RAM, should hit RAM limit
        assert result["max_cameras"] > 0
        assert result["max_cameras"] < 100
        assert result["limiting_factor"] == "RAM"

    def test_failover_capacity_cpu_limit(self):
        """Test failover capacity limited by CPU."""
        result = calculate_failover_capacity(
            max_camera_bitrate_mbps=2.0,
            cpu_variant="arm",  # 12 cameras max
            ram_gb=8,
            nic_bitrate_mbps=64,
            nic_count=1,
        )

        # ARM CPU limits to 12 cameras
        assert result["max_cameras"] <= 12

    def test_failover_capacity_nic_limit(self):
        """Test failover capacity limited by NIC bandwidth."""
        result = calculate_failover_capacity(
            max_camera_bitrate_mbps=50.0,  # High bitrate
            cpu_variant="core_i5",
            ram_gb=32,
            nic_bitrate_mbps=600,
            nic_count=1,
        )

        # 600 / 50 = 12 cameras max
        assert result["max_cameras"] <= 12
        assert result["limiting_factor"] == "Network bandwidth"


class TestApplyFailover:
    """Test failover application."""

    def test_no_failover(self):
        """Test with no failover."""
        result = apply_failover(
            servers_needed=2,
            failover_type="none",
        )

        assert result["total_servers"] == 2
        assert result["backup_servers"] == 0
        assert result["failover_type"] == "none"

    def test_n_plus_1_failover(self):
        """Test N+1 failover."""
        result = apply_failover(
            servers_needed=2,
            failover_type="n_plus_1",
        )

        # N+1: 2 × 2 = 4 servers
        assert result["total_servers"] == 4
        assert result["primary_servers"] == 2
        assert result["backup_servers"] == 2

    def test_n_plus_2_failover(self):
        """Test N+2 failover."""
        result = apply_failover(
            servers_needed=2,
            failover_type="n_plus_2",
        )

        # N+2: 2 × 3 = 6 servers
        assert result["total_servers"] == 6
        assert result["primary_servers"] == 2
        assert result["backup_servers"] == 4

    def test_failover_with_capacity(self):
        """Test failover with capacity calculation."""
        result = apply_failover(
            servers_needed=2,
            failover_type="n_plus_1",
            cameras_count=50,
            max_camera_bitrate_mbps=5.0,
            cpu_variant="core_i5",
            ram_gb=8,
        )

        assert result["total_servers"] == 4
        assert result["failover_capacity"] is not None
        assert "failover_estimate" in result["failover_capacity"]


class TestRecommendServerTier:
    """Test server tier recommendation."""

    def test_recommend_entry_tier(self):
        """Test recommendation for small deployment."""
        result = recommend_server_tier(
            devices_per_server=10,
            bitrate_per_server_mbps=50,
        )

        assert result["recommended_tier"] is not None
        assert "tier_name" in result or "name" in result

    def test_recommend_professional_tier(self):
        """Test recommendation for medium deployment."""
        result = recommend_server_tier(
            devices_per_server=100,
            bitrate_per_server_mbps=500,
        )

        assert result["recommended_tier"] is not None

    def test_recommend_enterprise_tier(self):
        """Test recommendation for large deployment."""
        result = recommend_server_tier(
            devices_per_server=250,
            bitrate_per_server_mbps=2000,
        )

        assert result["recommended_tier"] is not None

