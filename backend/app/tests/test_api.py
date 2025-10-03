"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and root endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Nx System Calculator API"
        assert data["status"] == "operational"

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestConfigEndpoints:
    """Test configuration endpoints."""

    def test_get_resolutions(self):
        """Test get resolutions endpoint."""
        response = client.get("/api/v1/config/resolutions")
        assert response.status_code == 200
        data = response.json()
        assert "resolutions" in data
        assert len(data["resolutions"]) > 0
        
        # Check first resolution has required fields
        res = data["resolutions"][0]
        assert "id" in res
        assert "name" in res
        assert "width" in res
        assert "height" in res
        assert "area" in res

    def test_get_codecs(self):
        """Test get codecs endpoint."""
        response = client.get("/api/v1/config/codecs")
        assert response.status_code == 200
        data = response.json()
        assert "codecs" in data
        assert len(data["codecs"]) > 0
        
        # Check first codec has required fields
        codec = data["codecs"][0]
        assert "id" in codec
        assert "name" in codec
        assert "compression_factor" in codec
        assert "quality_multipliers" in codec

    def test_get_raid_types(self):
        """Test get RAID types endpoint."""
        response = client.get("/api/v1/config/raid-types")
        assert response.status_code == 200
        data = response.json()
        assert "raid_types" in data
        assert len(data["raid_types"]) > 0
        
        # Check first RAID type has required fields
        raid = data["raid_types"][0]
        assert "id" in raid
        assert "name" in raid
        assert "usable_percentage" in raid

    def test_get_server_specs(self):
        """Test get server specs endpoint."""
        response = client.get("/api/v1/config/server-specs")
        assert response.status_code == 200
        data = response.json()
        assert "constraints" in data
        assert "server_tiers" in data


class TestCalculateEndpoint:
    """Test calculation endpoint."""

    def test_basic_calculation(self):
        """Test basic calculation with valid input."""
        request_data = {
            "project": {
                "project_name": "Test Project",
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
        }

        response = client.post("/api/v1/calculate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check response structure
        assert "project" in data
        assert "summary" in data
        assert "bitrate" in data
        assert "storage" in data
        assert "servers" in data
        assert "bandwidth" in data
        assert "licenses" in data
        
        # Check summary values
        assert data["summary"]["total_devices"] == 100
        assert data["summary"]["servers_needed"] > 0
        assert data["summary"]["total_storage_tb"] > 0
        assert data["summary"]["total_bitrate_mbps"] > 0

    def test_multiple_camera_groups(self):
        """Test calculation with multiple camera groups."""
        request_data = {
            "project": {
                "project_name": "Multi-Group Test",
                "created_by": "Test User",
                "creator_email": "test@example.com",
            },
            "camera_groups": [
                {
                    "num_cameras": 50,
                    "resolution_id": "2mp_1080p",
                    "fps": 30,
                    "codec_id": "h264",
                    "quality": "medium",
                    "recording_mode": "continuous",
                    "audio_enabled": False,
                },
                {
                    "num_cameras": 30,
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

        response = client.post("/api/v1/calculate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["summary"]["total_devices"] == 80

    def test_high_device_count(self):
        """Test calculation with high device count."""
        request_data = {
            "project": {
                "project_name": "Large Deployment",
                "created_by": "Test User",
                "creator_email": "test@example.com",
            },
            "camera_groups": [
                {
                    "num_cameras": 500,
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
                "nic_capacity_mbps": 10000,
                "nic_count": 2,
            },
        }

        response = client.post("/api/v1/calculate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["summary"]["total_devices"] == 500
        # Should need multiple servers
        assert data["servers"]["servers_needed"] >= 2

    def test_missing_required_fields(self):
        """Test calculation with missing required fields."""
        request_data = {
            "project": {
                "project_name": "Test",
            },
            "camera_groups": [],
            "retention_days": 30,
        }

        response = client.post("/api/v1/calculate", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_invalid_retention_days(self):
        """Test calculation with invalid retention days."""
        request_data = {
            "project": {
                "project_name": "Test",
                "created_by": "Test",
                "creator_email": "test@example.com",
            },
            "camera_groups": [
                {
                    "num_cameras": 10,
                    "resolution_id": "2mp_1080p",
                    "fps": 30,
                    "codec_id": "h264",
                    "quality": "medium",
                    "recording_mode": "continuous",
                    "audio_enabled": False,
                }
            ],
            "retention_days": 0,  # Invalid
            "server_config": {
                "raid_type": "raid5",
                "failover_type": "none",
                "nic_capacity_mbps": 1000,
                "nic_count": 1,
            },
        }

        response = client.post("/api/v1/calculate", json=request_data)
        assert response.status_code == 422

    def test_invalid_codec(self):
        """Test calculation with invalid codec."""
        request_data = {
            "project": {
                "project_name": "Test",
                "created_by": "Test",
                "creator_email": "test@example.com",
            },
            "camera_groups": [
                {
                    "num_cameras": 10,
                    "resolution_id": "2mp_1080p",
                    "fps": 30,
                    "codec_id": "invalid_codec",
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

        response = client.post("/api/v1/calculate", json=request_data)
        assert response.status_code == 400


class TestAPIDocumentation:
    """Test API documentation endpoints."""

    def test_openapi_schema(self):
        """Test OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_docs_endpoint(self):
        """Test Swagger UI docs endpoint."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc_endpoint(self):
        """Test ReDoc endpoint."""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

