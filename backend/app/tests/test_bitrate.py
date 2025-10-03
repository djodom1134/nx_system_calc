"""Unit tests for bitrate calculation module."""

import pytest
from app.services.calculations.bitrate import (
    calculate_bitrate,
    calculate_bitrate_manual,
    estimate_bitrate_from_preset,
    validate_bitrate_parameters,
)


class TestCalculateBitrate:
    """Test bitrate calculation function."""

    def test_basic_calculation(self):
        """Test basic bitrate calculation with new power function formula."""
        # 1080p @ 30fps with H.264 (compression_factor=0.10)
        # New formula: resolutionFactor = 0.009 × area^0.7
        # result = brandFactor × qualityFactor × fps × resolutionFactor × codecRatio
        # bitrate = result / 1024
        area = 1920 * 1080
        resolution_factor = 0.009 * (area ** 0.7)
        # brandFactor=1.0, qualityFactor=1.0, fps=30, codecRatio=0.10
        expected_result = 1.0 * 1.0 * 30 * resolution_factor * 0.10
        expected_bitrate = expected_result / 1024

        result = calculate_bitrate(
            resolution_area=area,
            fps=30,
            compression_factor=0.10,
            quality_multiplier=1.0,
            codec_id="h264",
        )
        assert result > 0
        assert isinstance(result, float)
        # Should match the power function formula
        assert abs(result - expected_bitrate) < 0.1

    def test_with_audio(self):
        """Test bitrate calculation with audio."""
        result_without_audio = calculate_bitrate(
            resolution_area=1920 * 1080,
            fps=30,
            compression_factor=0.10,
            audio_enabled=False,
        )
        result_with_audio = calculate_bitrate(
            resolution_area=1920 * 1080,
            fps=30,
            compression_factor=0.10,
            audio_enabled=True,
            audio_bitrate_kbps=64.0,
        )
        assert result_with_audio == result_without_audio + 64.0

    def test_quality_multipliers(self):
        """Test different quality levels with new quality factor range."""
        # Quality multipliers are now in range 0.1-1.0
        # Legacy multipliers (0.6-2.0) are auto-converted
        base_result = calculate_bitrate(
            resolution_area=1920 * 1080,
            fps=30,
            compression_factor=0.10,
            quality_multiplier=0.55,  # Medium quality (0.1-1.0 range)
            codec_id="h264",
        )

        high_quality = calculate_bitrate(
            resolution_area=1920 * 1080,
            fps=30,
            compression_factor=0.10,
            quality_multiplier=0.82,  # High quality (0.1-1.0 range)
            codec_id="h264",
        )

        # Higher quality should produce higher bitrate
        assert high_quality > base_result

    def test_h265_vs_h264(self):
        """Test H.265 produces lower bitrate than H.264 with same formula."""
        # Both H.264 and H.265 use the same power function formula
        # Difference is in compression_factor (codecRatio)
        h264_bitrate = calculate_bitrate(
            resolution_area=3840 * 2160,  # 4K
            fps=30,
            compression_factor=0.10,  # H.264
            codec_id="h264",
        )

        h265_bitrate = calculate_bitrate(
            resolution_area=3840 * 2160,  # 4K
            fps=30,
            compression_factor=0.07,  # H.265 (better compression)
            codec_id="h265",
        )

        # H.265 should have lower bitrate due to better compression
        assert h265_bitrate < h264_bitrate
        # Ratio should be approximately 0.7 (compression factor ratio)
        assert abs(h265_bitrate / h264_bitrate - 0.7) < 0.01

    def test_invalid_resolution(self):
        """Test validation for invalid resolution."""
        with pytest.raises(ValueError, match="Resolution area must be positive"):
            calculate_bitrate(
                resolution_area=0,
                fps=30,
                compression_factor=0.10,
            )

    def test_invalid_fps(self):
        """Test validation for invalid FPS."""
        with pytest.raises(ValueError, match="FPS must be between 1 and 100"):
            calculate_bitrate(
                resolution_area=1920 * 1080,
                fps=0,
                compression_factor=0.10,
            )

        with pytest.raises(ValueError, match="FPS must be between 1 and 100"):
            calculate_bitrate(
                resolution_area=1920 * 1080,
                fps=101,
                compression_factor=0.10,
            )

    def test_invalid_compression_factor(self):
        """Test validation for invalid compression factor."""
        with pytest.raises(ValueError, match="Compression factor must be positive"):
            calculate_bitrate(
                resolution_area=1920 * 1080,
                fps=30,
                compression_factor=0,
            )

    def test_edge_case_minimum_values(self):
        """Test edge case with low but realistic values."""
        # With power function, use realistic minimum values
        # VGA @ 15fps with low quality (typical for low-end cameras)
        result = calculate_bitrate(
            resolution_area=640 * 480,  # VGA
            fps=15,
            compression_factor=0.10,  # H.264
            quality_multiplier=0.1,  # Low quality
            codec_id="h264",
        )
        assert result > 0
        assert result < 50  # Should be very low bitrate

    def test_edge_case_maximum_values(self):
        """Test edge case with maximum valid values."""
        result = calculate_bitrate(
            resolution_area=16000000,  # 16MP
            fps=100,
            compression_factor=0.35,  # MJPEG
            quality_multiplier=2.0,  # Best quality
        )
        assert result > 0


class TestCalculateBitrateManual:
    """Test manual bitrate specification."""

    def test_manual_bitrate(self):
        """Test manual bitrate without audio."""
        result = calculate_bitrate_manual(bitrate_kbps=5000)
        assert result == 5000

    def test_manual_bitrate_with_audio(self):
        """Test manual bitrate with audio."""
        result = calculate_bitrate_manual(
            bitrate_kbps=5000,
            audio_enabled=True,
            audio_bitrate_kbps=64,
        )
        assert result == 5064

    def test_invalid_manual_bitrate(self):
        """Test validation for invalid manual bitrate."""
        with pytest.raises(ValueError, match="Bitrate must be positive"):
            calculate_bitrate_manual(bitrate_kbps=0)


class TestEstimateBitrateFromPreset:
    """Test bitrate estimation from presets."""

    def test_1080p_h264_medium(self):
        """Test 1080p with H.264 medium quality."""
        result = estimate_bitrate_from_preset(
            resolution_id="2mp_1080p",
            fps=30,
            codec_id="h264",
            quality="medium",
        )
        assert result > 0
        assert isinstance(result, float)

    def test_4k_h265_high(self):
        """Test 4K with H.265 high quality."""
        result = estimate_bitrate_from_preset(
            resolution_id="8mp_4k",
            fps=30,
            codec_id="h265",
            quality="high",
        )
        assert result > 0

    def test_invalid_resolution_id(self):
        """Test invalid resolution ID."""
        with pytest.raises(ValueError, match="Resolution not found"):
            estimate_bitrate_from_preset(
                resolution_id="invalid_resolution",
                fps=30,
                codec_id="h264",
            )

    def test_invalid_codec_id(self):
        """Test invalid codec ID."""
        with pytest.raises(ValueError, match="Codec not found"):
            estimate_bitrate_from_preset(
                resolution_id="2mp_1080p",
                fps=30,
                codec_id="invalid_codec",
            )


class TestValidateBitrateParameters:
    """Test parameter validation."""

    def test_valid_calculated_mode(self):
        """Test validation in calculated mode."""
        assert validate_bitrate_parameters(
            resolution_area=1920 * 1080,
            fps=30,
        )

    def test_valid_manual_mode(self):
        """Test validation in manual mode."""
        assert validate_bitrate_parameters(bitrate_kbps=5000)

    def test_missing_parameters_calculated_mode(self):
        """Test missing parameters in calculated mode."""
        with pytest.raises(ValueError, match="Resolution and FPS required"):
            validate_bitrate_parameters(resolution_area=1920 * 1080)

    def test_invalid_manual_bitrate(self):
        """Test invalid manual bitrate."""
        with pytest.raises(ValueError, match="Manual bitrate must be positive"):
            validate_bitrate_parameters(bitrate_kbps=0)


# Property-based tests using Hypothesis
try:
    from hypothesis import given, strategies as st

    class TestBitrateProperties:
        """Property-based tests for bitrate calculations."""

        @given(
            resolution_area=st.integers(min_value=1, max_value=16000000),
            fps=st.integers(min_value=1, max_value=100),
            compression_factor=st.floats(min_value=0.01, max_value=0.5),
        )
        def test_bitrate_always_positive(self, resolution_area, fps, compression_factor):
            """Bitrate should always be positive."""
            result = calculate_bitrate(resolution_area, fps, compression_factor)
            assert result > 0

        @given(
            resolution_area=st.integers(min_value=1, max_value=16000000),
            fps=st.integers(min_value=1, max_value=100),
        )
        def test_higher_fps_increases_bitrate(self, resolution_area, fps):
            """Higher FPS should increase bitrate."""
            if fps < 100:
                lower_fps = calculate_bitrate(resolution_area, fps, 0.10)
                higher_fps = calculate_bitrate(resolution_area, fps + 1, 0.10)
                assert higher_fps > lower_fps

except ImportError:
    # Hypothesis not installed, skip property-based tests
    pass

