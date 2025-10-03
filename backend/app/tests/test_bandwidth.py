"""Unit tests for bandwidth calculation module."""

import pytest
from app.services.calculations.bandwidth import (
    calculate_total_bandwidth,
    calculate_required_nics,
    validate_nic_capacity,
    recommend_nic_configuration,
)


class TestCalculateTotalBandwidth:
    """Test total bandwidth calculation."""

    def test_basic_bandwidth(self):
        """Test basic bandwidth calculation."""
        result = calculate_total_bandwidth(
            camera_bitrate_mbps=5.0,
            num_cameras=10,
        )
        
        # 10 cameras × 5 Mbps = 50 Mbps
        assert result["total_ingress_mbps"] == 50.0
        assert result["total_bandwidth_mbps"] >= 50.0

    def test_bandwidth_with_egress(self):
        """Test bandwidth with client egress."""
        result = calculate_total_bandwidth(
            camera_bitrate_mbps=5.0,
            num_cameras=10,
            num_clients=2,
            client_bitrate_mbps=10.0,
        )
        
        # Ingress: 10 × 5 = 50 Mbps
        # Egress: 2 × 10 = 20 Mbps
        assert result["total_ingress_mbps"] == 50.0
        assert result["total_egress_mbps"] == 20.0
        assert result["total_bandwidth_mbps"] == 70.0

    def test_bandwidth_with_overhead(self):
        """Test bandwidth includes overhead."""
        result = calculate_total_bandwidth(
            camera_bitrate_mbps=5.0,
            num_cameras=10,
            overhead_factor=0.2,  # 20% overhead
        )
        
        # 50 Mbps × 1.2 = 60 Mbps
        assert result["total_bandwidth_mbps"] == 60.0

    def test_zero_cameras(self):
        """Test with zero cameras."""
        result = calculate_total_bandwidth(
            camera_bitrate_mbps=5.0,
            num_cameras=0,
        )
        
        assert result["total_ingress_mbps"] == 0.0
        assert result["total_bandwidth_mbps"] == 0.0


class TestCalculateRequiredNICs:
    """Test required NIC calculation."""

    def test_single_nic_sufficient(self):
        """Test when single NIC is sufficient."""
        result = calculate_required_nics(
            max_bitrate_mbps=500,
            nic_bitrate_mbps=1000,  # 1 Gbps
            client_bitrate_mbps=0,
        )
        
        # 500 / 1000 = 0.5 → 1 NIC
        assert result["required_nics"] == 1

    def test_multiple_nics_required(self):
        """Test when multiple NICs required."""
        result = calculate_required_nics(
            max_bitrate_mbps=1500,
            nic_bitrate_mbps=1000,
            client_bitrate_mbps=0,
        )
        
        # 1500 / 1000 = 1.5 → 2 NICs
        assert result["required_nics"] == 2

    def test_with_client_bitrate(self):
        """Test NIC calculation includes client bitrate."""
        result = calculate_required_nics(
            max_bitrate_mbps=800,
            nic_bitrate_mbps=1000,
            client_bitrate_mbps=300,
        )
        
        # (800 + 300) / 1000 = 1.1 → 2 NICs
        assert result["required_nics"] == 2
        assert result["total_bitrate_mbps"] == 1100

    def test_arm_nic_bitrate(self):
        """Test with ARM NIC bitrate (64 Mbps)."""
        result = calculate_required_nics(
            max_bitrate_mbps=100,
            nic_bitrate_mbps=64,  # ARM
            client_bitrate_mbps=0,
        )
        
        # 100 / 64 = 1.56 → 2 NICs
        assert result["required_nics"] == 2

    def test_exact_multiple(self):
        """Test when bitrate is exact multiple of NIC capacity."""
        result = calculate_required_nics(
            max_bitrate_mbps=2000,
            nic_bitrate_mbps=1000,
            client_bitrate_mbps=0,
        )
        
        # 2000 / 1000 = 2.0 → 2 NICs
        assert result["required_nics"] == 2


class TestValidateNICCapacity:
    """Test NIC capacity validation."""

    def test_sufficient_capacity(self):
        """Test validation passes with sufficient capacity."""
        result = validate_nic_capacity(
            total_bitrate_mbps=500,
            nic_capacity_mbps=1000,
            nic_count=1,
        )
        
        assert result["is_valid"] is True
        assert result["utilization_percent"] == 50.0

    def test_insufficient_capacity(self):
        """Test validation fails with insufficient capacity."""
        result = validate_nic_capacity(
            total_bitrate_mbps=1500,
            nic_capacity_mbps=1000,
            nic_count=1,
        )
        
        assert result["is_valid"] is False
        assert result["utilization_percent"] == 150.0

    def test_multiple_nics(self):
        """Test validation with multiple NICs."""
        result = validate_nic_capacity(
            total_bitrate_mbps=1500,
            nic_capacity_mbps=1000,
            nic_count=2,
        )
        
        # Total capacity: 2 × 1000 = 2000 Mbps
        # Utilization: 1500 / 2000 = 75%
        assert result["is_valid"] is True
        assert result["utilization_percent"] == 75.0

    def test_with_headroom(self):
        """Test validation with headroom requirement."""
        result = validate_nic_capacity(
            total_bitrate_mbps=900,
            nic_capacity_mbps=1000,
            nic_count=1,
            headroom_percent=20,  # Require 20% headroom
        )
        
        # 900 / 1000 = 90% utilization
        # With 20% headroom requirement, max allowed is 80%
        assert result["is_valid"] is False

    def test_exact_capacity(self):
        """Test when bitrate exactly matches capacity."""
        result = validate_nic_capacity(
            total_bitrate_mbps=1000,
            nic_capacity_mbps=1000,
            nic_count=1,
        )
        
        assert result["utilization_percent"] == 100.0
        # Should be invalid (no headroom)
        assert result["is_valid"] is False


class TestRecommendNICConfiguration:
    """Test NIC configuration recommendation."""

    def test_recommend_single_1gbps(self):
        """Test recommendation for low bandwidth."""
        result = recommend_nic_configuration(
            total_bitrate_mbps=500,
        )
        
        assert result["recommended_nic_count"] >= 1
        assert result["recommended_nic_speed_mbps"] in [1000, 10000]

    def test_recommend_multiple_1gbps(self):
        """Test recommendation for medium bandwidth."""
        result = recommend_nic_configuration(
            total_bitrate_mbps=1500,
        )
        
        # Should recommend either 2×1Gbps or 1×10Gbps
        assert result["recommended_nic_count"] >= 1

    def test_recommend_10gbps(self):
        """Test recommendation for high bandwidth."""
        result = recommend_nic_configuration(
            total_bitrate_mbps=5000,
        )
        
        # Should recommend 10Gbps NIC(s)
        assert result["recommended_nic_speed_mbps"] >= 1000

    def test_recommendation_includes_headroom(self):
        """Test recommendation includes headroom."""
        result = recommend_nic_configuration(
            total_bitrate_mbps=800,
            headroom_percent=20,
        )
        
        # With 20% headroom, 800 Mbps needs 1000 Mbps capacity
        # Should recommend at least 1×1Gbps
        assert result["recommended_nic_count"] >= 1
        assert result["total_capacity_mbps"] >= 1000

    def test_recommendation_with_max_bitrate(self):
        """Test recommendation uses max bitrate for planning."""
        result = recommend_nic_configuration(
            total_bitrate_mbps=500,  # Average
            max_bitrate_mbps=800,    # Peak
        )
        
        # Should plan for peak (800 Mbps), not average
        assert result["total_capacity_mbps"] >= 800


class TestBandwidthEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_bitrate(self):
        """Test with zero bitrate."""
        result = calculate_total_bandwidth(
            camera_bitrate_mbps=0,
            num_cameras=10,
        )
        
        assert result["total_bandwidth_mbps"] == 0.0

    def test_very_high_bitrate(self):
        """Test with very high bitrate (8K cameras)."""
        result = calculate_total_bandwidth(
            camera_bitrate_mbps=100.0,  # 8K camera
            num_cameras=50,
        )
        
        # 50 × 100 = 5000 Mbps
        assert result["total_ingress_mbps"] == 5000.0

    def test_fractional_bitrate(self):
        """Test with fractional bitrate values."""
        result = calculate_total_bandwidth(
            camera_bitrate_mbps=2.5,
            num_cameras=7,
        )
        
        # 7 × 2.5 = 17.5 Mbps
        assert result["total_ingress_mbps"] == 17.5

    def test_single_camera(self):
        """Test with single camera."""
        result = calculate_total_bandwidth(
            camera_bitrate_mbps=5.0,
            num_cameras=1,
        )
        
        assert result["total_ingress_mbps"] == 5.0

    def test_max_cameras_per_server(self):
        """Test with maximum cameras per server (256)."""
        result = calculate_total_bandwidth(
            camera_bitrate_mbps=5.0,
            num_cameras=256,
        )
        
        # 256 × 5 = 1280 Mbps
        assert result["total_ingress_mbps"] == 1280.0


# Property-based tests
try:
    from hypothesis import given, strategies as st

    class TestBandwidthProperties:
        """Property-based tests for bandwidth calculations."""

        @given(
            bitrate=st.floats(min_value=0.1, max_value=100.0),
            cameras=st.integers(min_value=1, max_value=256),
        )
        def test_bandwidth_scales_linearly(self, bitrate, cameras):
            """Total bandwidth should scale linearly with camera count."""
            result = calculate_total_bandwidth(bitrate, cameras)
            expected = bitrate * cameras
            assert abs(result["total_ingress_mbps"] - expected) < 0.01

        @given(
            bitrate=st.floats(min_value=1.0, max_value=10000.0),
            nic_capacity=st.integers(min_value=100, max_value=10000),
        )
        def test_nic_count_always_positive(self, bitrate, nic_capacity):
            """Required NIC count should always be at least 1."""
            result = calculate_required_nics(bitrate, nic_capacity, 0)
            assert result["required_nics"] >= 1

except ImportError:
    # Hypothesis not installed
    pass

