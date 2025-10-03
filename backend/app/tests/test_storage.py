"""Unit tests for storage calculation module."""

import pytest
from app.services.calculations.storage import (
    calculate_daily_storage,
    calculate_storage,
    calculate_storage_with_hours,
    get_recording_factor,
    calculate_total_storage_multi_camera,
)


class TestCalculateDailyStorage:
    """Test daily storage calculation."""

    def test_continuous_recording(self):
        """Test continuous recording (24/7)."""
        # 1000 Kbps for 24 hours
        result = calculate_daily_storage(bitrate_kbps=1000, recording_factor=1.0)
        # Expected: (1000 * 86400) / (8 * 1024 * 1024) = 10.3 GB (rounded)
        assert result == 10.3

    def test_motion_recording(self):
        """Test motion detection recording (30% of time)."""
        result = calculate_daily_storage(bitrate_kbps=1000, recording_factor=0.3)
        # Expected: 10.3 * 0.3 = 3.09 GB (rounded)
        assert result == 3.09

    def test_zero_bitrate(self):
        """Test with zero bitrate raises error."""
        with pytest.raises(ValueError, match="Bitrate must be positive"):
            calculate_daily_storage(bitrate_kbps=0, recording_factor=1.0)

    def test_high_bitrate(self):
        """Test with high bitrate (4K camera)."""
        # 20 Mbps = 20000 Kbps
        result = calculate_daily_storage(bitrate_kbps=20000, recording_factor=1.0)
        # Expected: (20000 * 86400) / (8 * 1024 * 1024) = 205.99 GB (rounded)
        assert result == 205.99


class TestCalculateStorage:
    """Test total storage calculation."""

    def test_basic_calculation(self):
        """Test basic storage calculation."""
        # 1000 Kbps, 30 days retention, continuous recording
        result = calculate_storage(
            bitrate_kbps=1000,
            retention_days=30,
            recording_factor=1.0,
        )
        # Expected: 10.3 GB/day * 30 days = 309.0 GB
        assert result == 309.0

    def test_multiple_cameras(self):
        """Test with multiple cameras."""
        result = calculate_storage(
            bitrate_kbps=1000,
            retention_days=30,
            recording_factor=1.0,
            num_cameras=10,
        )
        # Expected: 10.3 * 30 * 10 = 3090.0 GB
        assert result == 3090.0

    def test_motion_detection(self):
        """Test with motion detection."""
        result = calculate_storage(
            bitrate_kbps=1000,
            retention_days=30,
            recording_factor=0.3,
        )
        # Expected: 3.09 * 30 = 92.7 GB
        assert result == 92.7

    def test_long_retention(self):
        """Test with long retention period."""
        result = calculate_storage(
            bitrate_kbps=1000,
            retention_days=365,
            recording_factor=1.0,
        )
        # Expected: 10.3 * 365 = 3759.5 GB
        assert result == 3759.5

    def test_invalid_retention(self):
        """Test with invalid retention days."""
        with pytest.raises(ValueError, match="Retention days must be at least 1"):
            calculate_storage(
                bitrate_kbps=1000,
                retention_days=0,
                recording_factor=1.0,
            )


class TestCalculateStorageWithHours:
    """Test storage calculation with custom hours."""

    def test_12_hours_per_day(self):
        """Test with 12 hours per day recording."""
        result = calculate_storage_with_hours(
            bitrate_kbps=1000,
            retention_days=30,
            hours_per_day=12,
        )
        # Expected: 10.3 GB/day * 0.5 (12/24) * 30 days = 154.5 GB
        assert result == 154.5

    def test_8_hours_per_day(self):
        """Test with 8 hours per day (business hours)."""
        result = calculate_storage_with_hours(
            bitrate_kbps=1000,
            retention_days=30,
            hours_per_day=8,
        )
        # Expected: 10.3 GB/day * 0.333 (8/24) * 30 days = 102.9 GB
        assert result == 102.9

    def test_invalid_hours(self):
        """Test with invalid hours per day."""
        with pytest.raises(ValueError, match="Hours per day must be between 0 and 24"):
            calculate_storage_with_hours(
                bitrate_kbps=1000,
                retention_days=30,
                hours_per_day=25,
            )


class TestGetRecordingFactor:
    """Test recording factor calculation."""

    def test_continuous_mode(self):
        """Test continuous recording mode."""
        assert get_recording_factor("continuous") == 1.0

    def test_motion_mode(self):
        """Test motion detection mode."""
        assert get_recording_factor("motion") == 0.3

    def test_object_mode(self):
        """Test object detection mode."""
        assert get_recording_factor("object") == 0.2

    def test_scheduled_mode_default(self):
        """Test scheduled mode with default hours."""
        # Default 12 hours = 0.5
        assert get_recording_factor("scheduled") == 0.5

    def test_scheduled_mode_custom_hours(self):
        """Test scheduled mode with custom hours."""
        assert get_recording_factor("scheduled", custom_hours=8) == 8 / 24

    def test_invalid_mode(self):
        """Test invalid recording mode."""
        with pytest.raises(ValueError, match="Invalid recording mode"):
            get_recording_factor("invalid_mode")


class TestCalculateTotalStorageMultiCamera:
    """Test multi-camera storage calculation."""

    def test_single_camera_group(self):
        """Test with single camera group."""
        camera_configs = [
            {
                "bitrate_kbps": 1000,
                "num_cameras": 10,
                "retention_days": 30,
                "recording_factor": 1.0,
            }
        ]
        result = calculate_total_storage_multi_camera(camera_configs)
        # Expected: 10.3 GB/day * 30 days * 10 cameras = 3090.0 GB
        assert result["total_storage_gb"] == 3090.0

    def test_multiple_camera_groups(self):
        """Test with multiple camera groups."""
        camera_configs = [
            {
                "bitrate_kbps": 1000,
                "num_cameras": 10,
                "retention_days": 30,
                "recording_factor": 1.0,
            },
            {
                "bitrate_kbps": 5000,
                "num_cameras": 5,
                "retention_days": 30,
                "recording_factor": 0.3,
            },
        ]
        result = calculate_total_storage_multi_camera(camera_configs)
        # Group 1: 10.3 * 30 * 10 = 3090.0 GB
        # Group 2: 51.5 * 30 * 5 * 0.3 = 2317.5 GB
        # Total: 5407.5 GB
        assert result["total_storage_gb"] == 5407.5

    def test_mixed_recording_modes(self):
        """Test with mixed recording modes."""
        camera_configs = [
            {
                "bitrate_kbps": 1000,
                "num_cameras": 50,
                "retention_days": 30,
                "recording_factor": 1.0,  # continuous
            },
            {
                "bitrate_kbps": 2000,
                "num_cameras": 30,
                "retention_days": 30,
                "recording_factor": 0.3,  # motion
            },
            {
                "bitrate_kbps": 3000,
                "num_cameras": 20,
                "retention_days": 30,
                "recording_factor": 8 / 24,  # scheduled 8 hours
            },
        ]
        result = calculate_total_storage_multi_camera(camera_configs)
        assert result["total_storage_gb"] > 0
        # Verify it's a reasonable value
        assert result["total_storage_gb"] < 100000  # Less than 100 TB


# Property-based tests
try:
    from hypothesis import given, strategies as st

    class TestStorageProperties:
        """Property-based tests for storage calculations."""

        @given(
            bitrate=st.floats(min_value=100, max_value=50000),
            retention=st.integers(min_value=1, max_value=365),
        )
        def test_storage_always_positive(self, bitrate, retention):
            """Storage should always be positive."""
            result = calculate_storage(bitrate, retention, 1.0)
            assert result > 0

        @given(
            bitrate=st.floats(min_value=100, max_value=50000),
            retention=st.integers(min_value=1, max_value=365),
        )
        def test_more_retention_more_storage(self, bitrate, retention):
            """More retention days should mean more storage."""
            if retention < 365:
                storage1 = calculate_storage(bitrate, retention, 1.0)
                storage2 = calculate_storage(bitrate, retention + 1, 1.0)
                assert storage2 > storage1

        @given(
            bitrate=st.floats(min_value=100, max_value=50000),
            num_cameras=st.integers(min_value=1, max_value=100),
        )
        def test_more_cameras_more_storage(self, bitrate, num_cameras):
            """More cameras should mean more storage."""
            storage1 = calculate_storage(bitrate, 30, 1.0, num_cameras)
            storage2 = calculate_storage(bitrate, 30, 1.0, num_cameras + 1)
            assert storage2 > storage1

except ImportError:
    # Hypothesis not installed, skip property-based tests
    pass

