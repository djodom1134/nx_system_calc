"""Validation tests for core_calculations.md formulas.

This test suite validates that all calculations match the exact formulas
documented in /docs/core_calculations.md.
"""

import pytest
import math
from app.services.calculations.bitrate import (
    calculate_bitrate,
    calculate_max_bitrate,
)
from app.services.calculations.storage import (
    calculate_daily_storage,
    get_recording_factor,
)
from app.services.calculations.servers import (
    calculate_required_ram,
    calculate_storage_throughput_limit,
)
from app.services.calculations.bandwidth import (
    calculate_required_nics,
)


class TestBitrateFormulas:
    """Test bitrate calculations match core_calculations.md."""

    def test_h264_resolution_factor_power_function(self):
        """Test H.264 uses resolutionFactor = 0.009 × area^0.7."""
        # 1080p: 1920 × 1080 = 2,073,600 pixels
        area = 1920 * 1080
        expected_resolution_factor = 0.009 * (area ** 0.7)

        # Calculate bitrate with known parameters
        fps = 30
        codec_ratio = 0.10  # H.264
        quality_factor = 0.55  # medium
        brand_factor = 1.0

        # Expected: brandFactor × qualityFactor × fps × resolutionFactor × codecRatio / 1024
        expected_result = brand_factor * quality_factor * fps * expected_resolution_factor * codec_ratio
        expected_bitrate = expected_result / 1024

        actual_bitrate = calculate_bitrate(
            resolution_area=area,
            fps=fps,
            compression_factor=codec_ratio,
            quality_multiplier=quality_factor,
            codec_id="h264",
            brand_factor=brand_factor,
            audio_enabled=False,
        )

        # Should match within rounding tolerance
        assert abs(actual_bitrate - expected_bitrate) < 0.1

    def test_h265_uses_same_formula_as_h264(self):
        """Test H.265 uses same power function formula as H.264."""
        area = 3840 * 2160  # 4K
        fps = 15
        codec_ratio = 0.07  # H.265
        quality_factor = 0.82  # high

        expected_resolution_factor = 0.009 * (area ** 0.7)
        expected_result = 1.0 * quality_factor * fps * expected_resolution_factor * codec_ratio
        expected_bitrate = expected_result / 1024

        actual_bitrate = calculate_bitrate(
            resolution_area=area,
            fps=fps,
            compression_factor=codec_ratio,
            quality_multiplier=quality_factor,
            codec_id="h265",
            audio_enabled=False,
        )

        assert abs(actual_bitrate - expected_bitrate) < 0.1

    def test_mjpeg_uses_different_formula(self):
        """Test MJPEG uses: (area / 6666) × fps × quality × (codecRatio + 1/3) × 12."""
        area = 1920 * 1080
        fps = 30
        codec_ratio = 0.35  # MJPEG
        quality_factor = 0.55

        # Formula: (area / 6666) × fps × quality × (codecRatio + 1/3) × 12 / 1024
        expected_result = (area / 6666) * fps * quality_factor * (codec_ratio + 1/3) * 12
        expected_bitrate = expected_result / 1024

        actual_bitrate = calculate_bitrate(
            resolution_area=area,
            fps=fps,
            compression_factor=codec_ratio,
            quality_multiplier=quality_factor,
            codec_id="mjpeg",
            audio_enabled=False,
        )

        assert abs(actual_bitrate - expected_bitrate) < 0.1

    def test_quality_factor_range(self):
        """Test quality factor is in range 0.1 to 1.0."""
        # Quality factors should be between 0.1 (low) and 1.0 (best)
        area = 1920 * 1080
        fps = 30
        codec_ratio = 0.10

        # Test with quality = 0.1 (low end)
        bitrate_low = calculate_bitrate(area, fps, codec_ratio, 0.1, codec_id="h264")

        # Test with quality = 1.0 (high end)
        bitrate_high = calculate_bitrate(area, fps, codec_ratio, 1.0, codec_id="h264")

        # High quality should produce higher bitrate
        assert bitrate_high > bitrate_low

        # Ratio should be approximately 10x (1.0 / 0.1)
        ratio = bitrate_high / bitrate_low
        assert 9.0 < ratio < 11.0

    def test_max_bitrate_calculation(self):
        """Test maxCameraBitrate = bitrateOne() × (1 + lowMotionQuality/100)."""
        average_bitrate = 2000.0
        low_motion_quality = 20.0

        expected_max = average_bitrate * (1 + low_motion_quality / 100)
        actual_max = calculate_max_bitrate(average_bitrate, low_motion_quality)

        assert actual_max == expected_max
        assert actual_max == 2400.0


class TestStorageFormulas:
    """Test storage calculations match core_calculations.md."""

    def test_daily_storage_constants(self):
        """Test daily storage uses exact constants: 60×60×24 / (8×1024×1024)."""
        bitrate_kbps = 1000.0
        recording_factor = 1.0

        # Formula: bitrate × (60 × 60 × 24) / (8 × 1024 × 1024) × recording_factor
        seconds_per_day = 60 * 60 * 24  # 86400
        bytes_conversion = 8 * 1024 * 1024  # 8388608

        expected_storage = (bitrate_kbps * seconds_per_day) / bytes_conversion * recording_factor
        actual_storage = calculate_daily_storage(bitrate_kbps, recording_factor)

        assert abs(actual_storage - expected_storage) < 0.01

    def test_motion_value_mapping(self):
        """Test motionValue() is correctly mapped to recording_factor."""
        # Continuous = 1.0
        assert get_recording_factor("continuous") == 1.0

        # Motion = 0.3
        assert get_recording_factor("motion") == 0.3

        # Object = 0.2
        assert get_recording_factor("object") == 0.2

        # Scheduled = 0.5 (default 12 hours)
        assert get_recording_factor("scheduled") == 0.5

    def test_scheduled_hours_factor(self):
        """Test scheduled recording uses (hours/24) factor."""
        # 8 hours per day = 8/24 = 0.333...
        factor_8h = get_recording_factor("scheduled", custom_hours=8)
        assert abs(factor_8h - (8/24)) < 0.001

        # 12 hours per day = 12/24 = 0.5
        factor_12h = get_recording_factor("scheduled", custom_hours=12)
        assert abs(factor_12h - 0.5) < 0.001


class TestServerRAMFormulas:
    """Test server RAM calculations match core_calculations.md."""

    def test_ram_formula_components(self):
        """Test requiredRAM = ramOS + (hostClient ? clientRam : 0) + cameras × cameraRam."""
        num_cameras = 100
        cpu_variant = "core_i5"

        # Without client
        result_no_client = calculate_required_ram(num_cameras, cpu_variant, host_client=False)
        expected_no_client = 1024 + (100 * 40)  # ramOS + cameras × 40MB
        assert result_no_client["required_ram_mb"] == expected_no_client

        # With client
        result_with_client = calculate_required_ram(num_cameras, cpu_variant, host_client=True)
        expected_with_client = 1024 + 3072 + (100 * 40)  # ramOS + clientRam + cameras × 40MB
        assert result_with_client["required_ram_mb"] == expected_with_client

    def test_ram_constants(self):
        """Test RAM constants: 40MB/camera, 3072MB client, 128MB/1024MB OS."""
        # ARM: 128MB OS
        result_arm = calculate_required_ram(10, "arm", False)
        assert result_arm["breakdown"]["os_ram_mb"] == 128

        # Core i5: 1024MB OS
        result_i5 = calculate_required_ram(10, "core_i5", False)
        assert result_i5["breakdown"]["os_ram_mb"] == 1024

        # Camera RAM: 40MB per camera
        assert result_i5["breakdown"]["camera_ram_mb"] == 10 * 40

        # Client RAM: 3072MB
        result_client = calculate_required_ram(10, "core_i5", True)
        assert result_client["breakdown"]["client_ram_mb"] == 3072

    def test_ram_power_of_2_rounding(self):
        """Test memory sizing rounded to next power of 2, max 64GB."""
        # 100 cameras: 1024 + 4000 = 5024MB = ~5GB → rounds to 8GB
        result_100 = calculate_required_ram(100, "core_i5", False)
        assert result_100["rounded_ram_gb"] == 8

        # 500 cameras: 1024 + 20000 = 21024MB = ~21GB → rounds to 32GB
        result_500 = calculate_required_ram(500, "core_i5", False)
        assert result_500["rounded_ram_gb"] == 32

        # 1500 cameras: 1024 + 60000 = 61024MB = ~60GB → rounds to 64GB (max)
        result_1500 = calculate_required_ram(1500, "core_i5", False)
        assert result_1500["rounded_ram_gb"] == 64


class TestStorageThroughputFormulas:
    """Test storage throughput calculations match core_calculations.md."""

    def test_storage_count_formula(self):
        """Test storageCount = Math.ceil(bitrate / (1024 × 204))."""
        # Note: The formula in core_calculations.md appears to have bitrate in Kbps
        # but we're using Mbps, so we don't divide by 1024 again
        bitrate_mbps = 500.0
        storage_throughput = 204  # Mbit/s per device

        expected_count = math.ceil(bitrate_mbps / storage_throughput)
        result = calculate_storage_throughput_limit(bitrate_mbps, storage_throughput)

        assert result["storage_count"] == expected_count

    def test_storage_throughput_constant(self):
        """Test storage throughput constant is 204 Mbit/s."""
        bitrate_mbps = 408.0  # Exactly 2× throughput
        result = calculate_storage_throughput_limit(bitrate_mbps, 204)

        assert result["storage_count"] == 2
        assert result["throughput_per_device_mbps"] == 204


class TestNICFormulas:
    """Test NIC calculations match core_calculations.md."""

    def test_required_nics_formula(self):
        """Test requiredNICs = Math.ceil((maxBitrate + clientBitrate) / nicBitrate)."""
        max_bitrate = 500.0
        client_bitrate = 100.0
        nic_bitrate = 600.0

        expected_nics = math.ceil((max_bitrate + client_bitrate) / nic_bitrate)
        result = calculate_required_nics(max_bitrate, nic_bitrate, client_bitrate)

        assert result["required_nics"] == expected_nics
        assert result["required_nics"] == 1  # 600 / 600 = 1

    def test_nic_bitrate_values(self):
        """Test NIC bitrate values from CPU variants."""
        # ARM: 64 Mbit/s
        result_arm = calculate_required_nics(50, 64, 0)
        assert result_arm["nic_bitrate_mbps"] == 64

        # Atom/i3/i5: 600 Mbit/s
        result_i5 = calculate_required_nics(500, 600, 0)
        assert result_i5["nic_bitrate_mbps"] == 600


class TestFailoverCalculations:
    """Test failover capacity calculations match core_calculations.md."""

    def test_failover_iterative_logic(self):
        """Test failover uses iterative camera addition until resource limits."""
        from app.services.calculations.servers import calculate_failover_capacity

        # Test with limited RAM (should hit RAM limit first)
        capacity = calculate_failover_capacity(
            max_camera_bitrate_mbps=5.0,  # 5 Mbps per camera
            cpu_variant="core_i5",  # 256 cameras max
            ram_gb=4,  # Only 4GB RAM
            nic_bitrate_mbps=600,  # 600 Mbps NIC
            nic_count=1,
            host_client=False,
        )

        # With 4GB (4096MB) RAM, ramOS=1024MB, cameraRam=40MB
        # Available for cameras: 4096 - 1024 = 3072MB
        # Max cameras: 3072 / 40 = 76.8 → 76 cameras
        assert capacity["max_cameras"] <= 77
        assert capacity["limiting_factor"] == "RAM"

    def test_failover_cpu_limit(self):
        """Test failover respects CPU variant camera limits."""
        from app.services.calculations.servers import calculate_failover_capacity

        # Test with ARM CPU (12 cameras max)
        capacity = calculate_failover_capacity(
            max_camera_bitrate_mbps=2.0,
            cpu_variant="arm",  # 12 cameras max
            ram_gb=8,  # Plenty of RAM
            nic_bitrate_mbps=64,  # 64 Mbps NIC
            nic_count=1,
        )

        # Should hit CPU limit at 12 cameras
        assert capacity["max_cameras"] <= 12
        assert capacity["limiting_factor"] in ["CPU (camera limit)", "Network bandwidth"]

    def test_failover_nic_limit(self):
        """Test failover respects NIC bandwidth limits."""
        from app.services.calculations.servers import calculate_failover_capacity

        # Test with high bitrate cameras and limited NIC
        capacity = calculate_failover_capacity(
            max_camera_bitrate_mbps=50.0,  # 50 Mbps per camera (4K)
            cpu_variant="core_i5",
            ram_gb=32,  # Plenty of RAM
            nic_bitrate_mbps=600,  # 600 Mbps NIC
            nic_count=1,
        )

        # With 600 Mbps NIC and 50 Mbps per camera: 600/50 = 12 cameras max
        assert capacity["max_cameras"] <= 12
        assert capacity["limiting_factor"] == "Network bandwidth"

    def test_failover_estimate_formula(self):
        """Test failoverEstimate = Math.max(currentMaxCameras - 1, camerasCount)."""
        from app.services.calculations.servers import apply_failover

        # Test with known capacity
        result = apply_failover(
            servers_needed=2,
            failover_type="n_plus_1",
            cameras_count=50,
            max_camera_bitrate_mbps=5.0,
            cpu_variant="core_i5",
            ram_gb=8,
            nic_bitrate_mbps=600,
            nic_count=1,
        )

        assert result["total_servers"] == 4  # 2 × 2 for N+1
        assert result["failover_capacity"] is not None
        assert "failover_estimate" in result["failover_capacity"]
        assert "max_cameras_per_server" in result["failover_capacity"]

        # failoverEstimate should be max(currentMaxCameras - 1, camerasCount)
        max_cameras = result["failover_capacity"]["max_cameras_per_server"]
        failover_estimate = result["failover_capacity"]["failover_estimate"]
        assert failover_estimate == max(max_cameras - 1, 50)


# Property-based tests
try:
    from hypothesis import given, strategies as st

    class TestCalculationProperties:
        """Property-based tests for calculation invariants."""

        @given(
            area=st.integers(min_value=100000, max_value=20000000),
            fps=st.integers(min_value=1, max_value=60),
        )
        def test_higher_resolution_higher_bitrate(self, area, fps):
            """Higher resolution should produce higher bitrate."""
            bitrate_low = calculate_bitrate(area, fps, 0.10, 0.55, codec_id="h264")
            bitrate_high = calculate_bitrate(area * 2, fps, 0.10, 0.55, codec_id="h264")
            assert bitrate_high > bitrate_low

        @given(
            cameras=st.integers(min_value=1, max_value=500),
        )
        def test_more_cameras_more_ram(self, cameras):
            """More cameras should require more RAM."""
            result = calculate_required_ram(cameras, "core_i5", False)
            expected_camera_ram = cameras * 40
            assert result["breakdown"]["camera_ram_mb"] == expected_camera_ram

except ImportError:
    # Hypothesis not installed
    pass

