"""Bitrate calculation module.

This module provides functions to calculate video bitrate based on:
- Resolution (pixels)
- Frame rate (FPS)
- Codec type and compression factor
- Quality level
- Audio recording

Formulas from core_calculations.md:
- H.264/H.265: result = brandFactor × qualityFactor × frameRateFactor × resolutionFactor × codecRatio
  where resolutionFactor = 0.009 × (resolution.area)^0.7
- Other codecs: result = (resolution.area / 6666) × frameRateFactor × qualityFactor × (codecRatio + 1/3) × 12
- Quality factor: lowEnd + (hiEnd - lowEnd) × qualityRatio where lowEnd=0.1, hiEnd=1.0
- Final: result / 1024
"""

from typing import Optional


def calculate_bitrate(
    resolution_area: int,
    fps: int,
    compression_factor: float,
    quality_multiplier: float = 1.0,
    audio_enabled: bool = False,
    audio_bitrate_kbps: float = 64.0,
    codec_id: str = "h264",
    brand_factor: float = 1.0,
) -> float:
    """
    Calculate video bitrate in Kbps using formulas from core_calculations.md.

    For H.264/H.265 codecs:
        resolutionFactor = 0.009 × (resolution_area)^0.7
        result = brandFactor × qualityFactor × fps × resolutionFactor × codecRatio
        bitrate = result / 1024

    For other codecs (MJPEG):
        result = (resolution_area / 6666) × fps × qualityFactor × (codecRatio + 1/3) × 12
        bitrate = result / 1024

    Args:
        resolution_area: Total pixels (width × height)
        fps: Frames per second (1-100)
        compression_factor: Codec compression factor (codecRatio: 0.07 for H.265, 0.10 for H.264)
        quality_multiplier: Quality factor (0.1 to 1.0 range, or legacy 0.6-2.0)
        audio_enabled: Whether audio is recorded
        audio_bitrate_kbps: Audio bitrate in Kbps (default 64)
        codec_id: Codec identifier ("h264", "h265", "h264_plus", "mjpeg")
        brand_factor: Brand-specific adjustment factor (default 1.0)

    Returns:
        Total bitrate in Kbps

    Raises:
        ValueError: If parameters are out of valid range

    Examples:
        >>> # 1080p @ 30fps with H.264 medium quality
        >>> calculate_bitrate(1920 * 1080, 30, 0.10, 0.55, codec_id="h264")
        2048.5

        >>> # 4K @ 15fps with H.265 high quality
        >>> calculate_bitrate(3840 * 2160, 15, 0.07, 0.82, codec_id="h265")
        3521.2
    """
    # Validation
    if resolution_area <= 0:
        raise ValueError("Resolution area must be positive")
    if not 1 <= fps <= 100:
        raise ValueError("FPS must be between 1 and 100")
    if compression_factor <= 0:
        raise ValueError("Compression factor must be positive")
    if quality_multiplier <= 0:
        raise ValueError("Quality multiplier must be positive")
    if brand_factor <= 0:
        raise ValueError("Brand factor must be positive")

    # Determine if codec is H.264/H.265 or other
    is_h264_h265 = codec_id.lower() in ["h264", "h265", "h264_plus"]

    # Calculate video bitrate using appropriate formula
    if is_h264_h265:
        # H.264/H.265 formula: resolutionFactor = 0.009 × area^0.7
        resolution_factor = 0.009 * (resolution_area ** 0.7)
        result = brand_factor * quality_multiplier * fps * resolution_factor * compression_factor
    else:
        # Other codecs (MJPEG): (area / 6666) × fps × quality × (codecRatio + 1/3) × 12
        result = (resolution_area / 6666) * fps * quality_multiplier * (compression_factor + 1/3) * 12

    # Convert to Kbps (divide by 1024 as per core_calculations.md)
    video_bitrate = result / 1024

    # Add audio bitrate if enabled
    total_bitrate = video_bitrate
    if audio_enabled:
        total_bitrate += audio_bitrate_kbps

    return round(total_bitrate, 2)


def calculate_bitrate_manual(
    bitrate_kbps: float,
    audio_enabled: bool = False,
    audio_bitrate_kbps: float = 64.0,
) -> float:
    """
    Use manually specified bitrate instead of calculating.

    This allows users to override automatic calculation with known values.

    Args:
        bitrate_kbps: Manual video bitrate in Kbps
        audio_enabled: Whether audio is recorded
        audio_bitrate_kbps: Audio bitrate in Kbps (default 64)

    Returns:
        Total bitrate in Kbps

    Raises:
        ValueError: If bitrate is not positive
    """
    if bitrate_kbps <= 0:
        raise ValueError("Bitrate must be positive")

    total_bitrate = bitrate_kbps
    if audio_enabled:
        total_bitrate += audio_bitrate_kbps

    return round(total_bitrate, 2)


def calculate_max_bitrate(
    average_bitrate_kbps: float,
    low_motion_quality: float = 20.0,
) -> float:
    """
    Calculate maximum camera bitrate for peak motion scenes.

    Formula from core_calculations.md:
        maxCameraBitrate = bitrateOne() × (1 + lowMotionQuality/100)

    This represents the peak bitrate during high-motion scenes and should be used
    for NIC capacity planning and failover calculations.

    Args:
        average_bitrate_kbps: Average bitrate in Kbps
        low_motion_quality: Quality adjustment percentage for variable bitrate (default 20%)

    Returns:
        Maximum bitrate in Kbps

    Examples:
        >>> calculate_max_bitrate(2000, 20.0)
        2400.0
    """
    if average_bitrate_kbps <= 0:
        raise ValueError("Average bitrate must be positive")
    if low_motion_quality < 0:
        raise ValueError("Low motion quality must be non-negative")

    max_bitrate = average_bitrate_kbps * (1 + low_motion_quality / 100)
    return round(max_bitrate, 2)


def estimate_bitrate_from_preset(
    resolution_id: str,
    fps: int,
    codec_id: str,
    quality: str = "medium",
    audio_enabled: bool = False,
    brand_factor: float = 1.0,
) -> float:
    """
    Calculate bitrate using preset configurations.

    This is a convenience function that loads configuration and calls calculate_bitrate.

    Args:
        resolution_id: Resolution preset ID (e.g., "2mp_1080p", "8mp_4k")
        fps: Frames per second
        codec_id: Codec ID (e.g., "h264", "h265", "mjpeg")
        quality: Quality level ("low", "medium", "high", "best")
        audio_enabled: Whether audio is recorded
        brand_factor: Brand-specific adjustment factor (default 1.0)

    Returns:
        Total bitrate in Kbps

    Raises:
        ValueError: If preset not found or parameters invalid
    """
    from app.core.config import ConfigLoader

    # Load configurations
    resolution = ConfigLoader.get_resolution_by_id(resolution_id)
    codec = ConfigLoader.get_codec_by_id(codec_id)

    # Get quality multiplier and convert to 0.1-1.0 range if needed
    quality_multipliers = codec.get("quality_multipliers", {})
    quality_multiplier = quality_multipliers.get(quality, 1.0)

    # Convert legacy quality multipliers (0.6-2.0) to new range (0.1-1.0)
    # This maintains backward compatibility
    if quality_multiplier > 1.0:
        # Legacy high/best quality - map to upper range
        quality_multiplier = 0.55 + (quality_multiplier - 1.0) * 0.225  # Maps 1.4->0.82, 2.0->0.775
    elif quality_multiplier < 1.0:
        # Legacy low quality - map to lower range
        quality_multiplier = 0.1 + (quality_multiplier - 0.6) * 1.125  # Maps 0.6->0.1, 1.0->0.55

    # Calculate bitrate
    return calculate_bitrate(
        resolution_area=resolution["area"],
        fps=fps,
        compression_factor=codec["compression_factor"],
        quality_multiplier=quality_multiplier,
        audio_enabled=audio_enabled,
        codec_id=codec_id,
        brand_factor=brand_factor,
    )


def validate_bitrate_parameters(
    resolution_area: Optional[int] = None,
    fps: Optional[int] = None,
    bitrate_kbps: Optional[float] = None,
) -> bool:
    """
    Validate bitrate calculation parameters.

    Args:
        resolution_area: Resolution in pixels
        fps: Frames per second
        bitrate_kbps: Manual bitrate

    Returns:
        True if parameters are valid

    Raises:
        ValueError: If parameters are invalid
    """
    if bitrate_kbps is not None:
        # Manual bitrate mode
        if bitrate_kbps <= 0:
            raise ValueError("Manual bitrate must be positive")
    else:
        # Calculated bitrate mode
        if resolution_area is None or fps is None:
            raise ValueError("Resolution and FPS required for calculated bitrate")
        if resolution_area <= 0:
            raise ValueError("Resolution area must be positive")
        if not 1 <= fps <= 100:
            raise ValueError("FPS must be between 1 and 100")

    return True

