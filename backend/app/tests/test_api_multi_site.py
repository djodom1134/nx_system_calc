"""Tests for multi-site API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestMultiSiteAPI:
    """Tests for /api/v1/calculate/multi-site endpoint."""

    def test_single_site_deployment(self):
        """Test API with deployment fitting in single site."""
        request_data = {
            "project": {
                "project_name": "Single Site Test",
                "created_by": "Test User",
                "creator_email": "test@example.com",
            },
            "camera_groups": [
                {
                    "num_cameras": 100,
                    "resolution_id": "2mp_1080p",
                    "fps": 30,
                    "codec_id": "h264",
                    "quality": "medium",
                    "recording_mode": "continuous",
                    "audio_enabled": False,
                }
            ],
            "retention_days": 30,
            "server_config": {
                "raid_type": "raid5",
                "failover_type": "none",
                "nic_capacity_mbps": 1000,
                "nic_count": 1,
            },
            "max_devices_per_site": 2560,
            "max_servers_per_site": 10,
        }

        response = client.post("/api/v1/calculate/multi-site", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["summary"]["total_sites"] == 1
        assert data["summary"]["total_devices"] == 100
        assert len(data["sites"]) == 1
        assert data["sites"][0]["devices"] == 100
        assert data["all_sites_valid"] is True

    def test_multi_site_deployment(self):
        """Test API with deployment requiring multiple sites."""
        request_data = {
            "project": {
                "project_name": "Multi Site Test",
                "created_by": "Test User",
                "creator_email": "test@example.com",
            },
            "camera_groups": [
                {
                    "num_cameras": 3000,
                    "resolution_id": "2mp_1080p",
                    "fps": 30,
                    "codec_id": "h264",
                    "quality": "medium",
                    "recording_mode": "continuous",
                    "audio_enabled": False,
                }
            ],
            "retention_days": 30,
            "server_config": {
                "raid_type": "raid5",
                "failover_type": "none",
                "nic_capacity_mbps": 1000,
                "nic_count": 1,
            },
            "max_devices_per_site": 2560,
        }

        response = client.post("/api/v1/calculate/multi-site", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["summary"]["total_sites"] == 2
        assert data["summary"]["total_devices"] == 3000
        assert len(data["sites"]) == 2

        # Verify device distribution
        total_site_devices = sum(site["devices"] for site in data["sites"])
        assert total_site_devices == 3000

    def test_multiple_camera_groups(self):
        """Test API with multiple camera groups."""
        request_data = {
            "project": {
                "project_name": "Multi Group Multi Site",
                "created_by": "Test User",
                "creator_email": "test@example.com",
            },
            "camera_groups": [
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
            ],
            "retention_days": 30,
            "server_config": {
                "raid_type": "raid5",
                "failover_type": "none",
                "nic_capacity_mbps": 1000,
                "nic_count": 1,
            },
        }

        response = client.post("/api/v1/calculate/multi-site", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["summary"]["total_sites"] == 2
        assert data["summary"]["total_devices"] == 3000

    def test_large_deployment(self):
        """Test API with large multi-site deployment."""
        request_data = {
            "project": {
                "project_name": "Large Deployment",
                "created_by": "Test User",
                "creator_email": "test@example.com",
            },
            "camera_groups": [
                {
                    "num_cameras": 10000,
                    "resolution_id": "2mp_1080p",
                    "fps": 30,
                    "codec_id": "h264",
                    "quality": "medium",
                    "recording_mode": "continuous",
                    "audio_enabled": False,
                }
            ],
            "retention_days": 30,
            "server_config": {
                "raid_type": "raid5",
                "failover_type": "n_plus_1",
                "nic_capacity_mbps": 1000,
                "nic_count": 1,
            },
        }

        response = client.post("/api/v1/calculate/multi-site", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["summary"]["total_sites"] == 4  # 10000 / 2560 = 3.9 -> 4 sites
        assert data["summary"]["total_devices"] == 10000

        # Verify aggregate totals
        total_bitrate = sum(site["bitrate_mbps"] for site in data["sites"])
        total_storage = sum(site["storage_tb"] for site in data["sites"])
        total_servers = sum(site["servers_with_failover"] for site in data["sites"])

        assert abs(data["summary"]["total_bitrate_mbps"] - total_bitrate) < 0.1
        assert abs(data["summary"]["total_storage_tb"] - total_storage) < 0.1
        assert data["summary"]["total_servers"] == total_servers

    def test_custom_site_limits(self):
        """Test API with custom site limits."""
        request_data = {
            "project": {
                "project_name": "Custom Limits",
                "created_by": "Test User",
                "creator_email": "test@example.com",
            },
            "camera_groups": [
                {
                    "num_cameras": 600,
                    "resolution_id": "2mp_1080p",
                    "fps": 30,
                    "codec_id": "h264",
                    "quality": "medium",
                    "recording_mode": "continuous",
                    "audio_enabled": False,
                }
            ],
            "retention_days": 30,
            "server_config": {
                "raid_type": "raid5",
                "failover_type": "none",
                "nic_capacity_mbps": 1000,
                "nic_count": 1,
            },
            "max_devices_per_site": 500,  # Custom limit
            "max_servers_per_site": 5,
        }

        response = client.post("/api/v1/calculate/multi-site", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["summary"]["total_sites"] == 2  # 600 / 500 = 1.2 -> 2 sites
        assert data["summary"]["max_devices_per_site"] == 500

    def test_validation_warnings(self):
        """Test API returns warnings for high utilization."""
        request_data = {
            "project": {
                "project_name": "High Utilization",
                "created_by": "Test User",
                "creator_email": "test@example.com",
            },
            "camera_groups": [
                {
                    "num_cameras": 2400,  # 93.75% of 2560
                    "resolution_id": "2mp_1080p",
                    "fps": 30,
                    "codec_id": "h264",
                    "quality": "medium",
                    "recording_mode": "continuous",
                    "audio_enabled": False,
                }
            ],
            "retention_days": 30,
            "server_config": {
                "raid_type": "raid5",
                "failover_type": "none",
                "nic_capacity_mbps": 1000,
                "nic_count": 1,
            },
        }

        response = client.post("/api/v1/calculate/multi-site", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["summary"]["total_sites"] == 1
        # Should have warnings about high utilization
        assert len(data["warnings"]) > 0

    def test_missing_required_fields(self):
        """Test API with missing required fields."""
        request_data = {
            "project": {
                "project_name": "Test",
            },
            "camera_groups": [],
            "retention_days": 30,
        }

        response = client.post("/api/v1/calculate/multi-site", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_invalid_camera_config(self):
        """Test API with invalid camera configuration."""
        request_data = {
            "project": {
                "project_name": "Test",
                "created_by": "Test",
                "creator_email": "test@example.com",
            },
            "camera_groups": [
                {
                    "num_cameras": 0,  # Invalid
                    "resolution_id": "2mp_1080p",
                    "fps": 30,
                    "codec_id": "h264",
                }
            ],
            "retention_days": 30,
        }

        response = client.post("/api/v1/calculate/multi-site", json=request_data)
        assert response.status_code == 422  # Validation error

