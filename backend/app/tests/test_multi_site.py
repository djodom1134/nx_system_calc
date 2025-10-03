"""Tests for multi-site calculation module."""

import pytest
from app.services.calculations.multi_site import (
    calculate_sites_needed,
    validate_site_configuration,
    calculate_multi_site_deployment,
)


class TestCalculateSitesNeeded:
    """Tests for calculate_sites_needed function."""

    def test_single_site(self):
        """Test with devices fitting in single site."""
        result = calculate_sites_needed(total_devices=1000, max_devices_per_site=2560)
        
        assert result["sites_needed"] == 1
        assert result["devices_per_site"] == [1000]
        assert result["total_devices"] == 1000
        assert result["max_devices_per_site"] == 2560

    def test_exactly_one_site(self):
        """Test with exactly max devices for one site."""
        result = calculate_sites_needed(total_devices=2560, max_devices_per_site=2560)
        
        assert result["sites_needed"] == 1
        assert result["devices_per_site"] == [2560]

    def test_two_sites(self):
        """Test with devices requiring two sites."""
        result = calculate_sites_needed(total_devices=3000, max_devices_per_site=2560)
        
        assert result["sites_needed"] == 2
        assert result["devices_per_site"] == [2560, 440]
        assert sum(result["devices_per_site"]) == 3000

    def test_multiple_sites(self):
        """Test with devices requiring multiple sites."""
        result = calculate_sites_needed(total_devices=10000, max_devices_per_site=2560)
        
        assert result["sites_needed"] == 4
        assert result["devices_per_site"] == [2560, 2560, 2560, 2320]
        assert sum(result["devices_per_site"]) == 10000

    def test_exactly_multiple_sites(self):
        """Test with exactly multiple sites worth of devices."""
        result = calculate_sites_needed(total_devices=7680, max_devices_per_site=2560)
        
        assert result["sites_needed"] == 3
        assert result["devices_per_site"] == [2560, 2560, 2560]

    def test_small_site_limit(self):
        """Test with small site limit."""
        result = calculate_sites_needed(total_devices=100, max_devices_per_site=50)
        
        assert result["sites_needed"] == 2
        assert result["devices_per_site"] == [50, 50]

    def test_invalid_total_devices(self):
        """Test with invalid total devices."""
        with pytest.raises(ValueError, match="Total devices must be at least 1"):
            calculate_sites_needed(total_devices=0)

    def test_invalid_max_devices(self):
        """Test with invalid max devices per site."""
        with pytest.raises(ValueError, match="Max devices per site must be at least 1"):
            calculate_sites_needed(total_devices=100, max_devices_per_site=0)


class TestValidateSiteConfiguration:
    """Tests for validate_site_configuration function."""

    def test_valid_configuration(self):
        """Test with valid site configuration."""
        result = validate_site_configuration(
            devices_per_site=1000,
            servers_per_site=5,
            max_devices_per_site=2560,
            max_servers_per_site=10,
            max_devices_per_server=256,
        )
        
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        assert result["devices_per_site"] == 1000
        assert result["servers_per_site"] == 5

    def test_exceeds_device_limit(self):
        """Test with devices exceeding site limit."""
        result = validate_site_configuration(
            devices_per_site=3000,
            servers_per_site=12,
            max_devices_per_site=2560,
        )
        
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
        assert any("exceeds maximum" in err for err in result["errors"])

    def test_exceeds_server_limit(self):
        """Test with servers exceeding site limit."""
        result = validate_site_configuration(
            devices_per_site=2000,
            servers_per_site=15,
            max_servers_per_site=10,
        )
        
        assert result["is_valid"] is False
        assert any("servers" in err and "exceeds" in err for err in result["errors"])

    def test_insufficient_server_capacity(self):
        """Test with insufficient server capacity for devices."""
        result = validate_site_configuration(
            devices_per_site=1000,
            servers_per_site=2,
            max_devices_per_server=256,
        )
        
        assert result["is_valid"] is False
        assert any("max capacity" in err for err in result["errors"])

    def test_warning_high_utilization(self):
        """Test warning for high device utilization."""
        result = validate_site_configuration(
            devices_per_site=2400,  # 93.75% of 2560
            servers_per_site=10,
            max_devices_per_site=2560,
        )
        
        assert result["is_valid"] is True
        assert len(result["warnings"]) > 0
        assert any("capacity" in warn for warn in result["warnings"])

    def test_warning_high_server_count(self):
        """Test warning for high server count."""
        result = validate_site_configuration(
            devices_per_site=2000,
            servers_per_site=9,  # 90% of 10
            max_servers_per_site=10,
        )
        
        assert result["is_valid"] is True
        assert len(result["warnings"]) > 0

    def test_utilization_calculation(self):
        """Test utilization percentage calculation."""
        result = validate_site_configuration(
            devices_per_site=1280,  # 50% of 2560
            servers_per_site=5,
            max_devices_per_site=2560,
        )
        
        assert result["utilization_percent"] == 50.0


class TestCalculateMultiSiteDeployment:
    """Tests for calculate_multi_site_deployment function."""

    def test_single_site_deployment(self):
        """Test deployment fitting in single site."""
        camera_groups = [
            {
                "num_cameras": 100,
                "resolution_id": "2mp_1080p",
                "fps": 30,
                "codec_id": "h264",
                "quality": "medium",
                "recording_mode": "continuous",
                "audio_enabled": False,
            }
        ]
        
        result = calculate_multi_site_deployment(
            camera_groups=camera_groups,
            retention_days=30,
            server_config={
                "nic_capacity_mbps": 1000,
                "nic_count": 1,
                "failover_type": "none",
            },
            max_devices_per_site=2560,
        )
        
        assert result["summary"]["total_sites"] == 1
        assert result["summary"]["total_devices"] == 100
        assert len(result["sites"]) == 1
        assert result["sites"][0]["devices"] == 100
        assert result["all_sites_valid"] is True

    def test_multi_site_deployment(self):
        """Test deployment requiring multiple sites."""
        camera_groups = [
            {
                "num_cameras": 3000,
                "resolution_id": "2mp_1080p",
                "fps": 30,
                "codec_id": "h264",
                "quality": "medium",
                "recording_mode": "continuous",
                "audio_enabled": False,
            }
        ]
        
        result = calculate_multi_site_deployment(
            camera_groups=camera_groups,
            retention_days=30,
            server_config={
                "nic_capacity_mbps": 1000,
                "nic_count": 1,
                "failover_type": "none",
            },
            max_devices_per_site=2560,
        )
        
        assert result["summary"]["total_sites"] == 2
        assert result["summary"]["total_devices"] == 3000
        assert len(result["sites"]) == 2
        
        # Verify device distribution
        total_site_devices = sum(site["devices"] for site in result["sites"])
        assert total_site_devices == 3000

    def test_multiple_camera_groups(self):
        """Test with multiple camera groups."""
        camera_groups = [
            {
                "num_cameras": 1500,
                "resolution_id": "2mp_1080p",
                "fps": 30,
                "codec_id": "h264",
                "quality": "medium",
                "recording_mode": "continuous",
                "audio_enabled": False,
            },
            {
                "num_cameras": 1500,
                "resolution_id": "4mp",
                "fps": 15,
                "codec_id": "h265",
                "quality": "high",
                "recording_mode": "motion",
                "audio_enabled": True,
            },
        ]
        
        result = calculate_multi_site_deployment(
            camera_groups=camera_groups,
            retention_days=30,
            server_config={
                "nic_capacity_mbps": 1000,
                "nic_count": 1,
                "failover_type": "none",
            },
            max_devices_per_site=2560,
        )
        
        assert result["summary"]["total_sites"] == 2
        assert result["summary"]["total_devices"] == 3000

    def test_aggregate_calculations(self):
        """Test aggregate totals across sites."""
        camera_groups = [
            {
                "num_cameras": 5000,
                "resolution_id": "2mp_1080p",
                "fps": 30,
                "codec_id": "h264",
                "quality": "medium",
                "recording_mode": "continuous",
                "audio_enabled": False,
            }
        ]
        
        result = calculate_multi_site_deployment(
            camera_groups=camera_groups,
            retention_days=30,
            server_config={
                "nic_capacity_mbps": 1000,
                "nic_count": 1,
                "failover_type": "none",
            },
            max_devices_per_site=2560,
        )
        
        # Verify aggregate totals match sum of sites
        total_bitrate = sum(site["bitrate_mbps"] for site in result["sites"])
        total_storage = sum(site["storage_tb"] for site in result["sites"])
        total_servers = sum(site["servers_with_failover"] for site in result["sites"])
        
        assert abs(result["summary"]["total_bitrate_mbps"] - total_bitrate) < 0.1
        assert abs(result["summary"]["total_storage_tb"] - total_storage) < 0.1
        assert result["summary"]["total_servers"] == total_servers

