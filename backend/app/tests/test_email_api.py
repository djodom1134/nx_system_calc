"""Integration tests for email API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_smtp_settings(monkeypatch):
    """Mock SMTP settings."""
    monkeypatch.setenv("SMTP_HOST", "smtp.test.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "test@test.com")
    monkeypatch.setenv("SMTP_PASSWORD", "test-password")
    monkeypatch.setenv("SMTP_FROM", "noreply@test.com")
    monkeypatch.setenv("SMTP_BCC", "sales@test.com")

    # Force reload of settings
    from app.core.config import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def sample_email_calculation_request():
    """Sample email calculation request."""
    return {
        "calculation": {
            "project": {
                "project_name": "Test Project",
                "created_by": "John Doe",
                "creator_email": "john@example.com"
            },
            "camera_groups": [
                {
                    "num_cameras": 100,
                    "resolution_id": "4mp",
                    "fps": 30,
                    "codec_id": "h264",
                    "quality": "medium",
                    "recording_mode": "continuous",
                    "audio_enabled": False,
                    "bitrate_kbps": 4000
                }
            ],
            "retention_days": 30,
            "server_config": {
                "raid_type": "raid5",
                "failover_type": "none",
                "nic_capacity_mbps": 1000,
                "nic_count": 1
            }
        },
        "email": {
            "recipient_email": "customer@example.com",
            "recipient_name": "Jane Smith",
            "include_pdf": True
        }
    }


class TestEmailAPI:
    """Test email API endpoints."""

    def test_send_test_email(self, mock_smtp_settings):
        """Test sending test email."""
        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            response = client.post(
                "/api/v1/email/test",
                json={"recipient_email": "test@example.com"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "successfully" in data["message"]

    def test_send_test_email_invalid_email(self):
        """Test sending test email with invalid email address."""
        response = client.post(
            "/api/v1/email/test",
            json={"recipient_email": "invalid-email"}
        )

        assert response.status_code == 422  # Validation error

    def test_send_test_email_without_credentials(self):
        """Test sending test email without SMTP credentials."""
        # Don't mock settings
        response = client.post(
            "/api/v1/email/test",
            json={"recipient_email": "test@example.com"}
        )

        assert response.status_code == 500
        assert "credentials not configured" in response.json()["detail"]

    def test_send_calculation_report_email(self, mock_smtp_settings, sample_email_calculation_request):
        """Test sending calculation report email."""
        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            response = client.post(
                "/api/v1/email/send-report",
                json=sample_email_calculation_request
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "customer@example.com" in data["message"]

    def test_send_calculation_report_without_pdf(self, mock_smtp_settings, sample_email_calculation_request):
        """Test sending calculation report without PDF."""
        sample_email_calculation_request["email"]["include_pdf"] = False

        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            response = client.post(
                "/api/v1/email/send-report",
                json=sample_email_calculation_request
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_send_calculation_report_with_cc(self, mock_smtp_settings, sample_email_calculation_request):
        """Test sending calculation report with CC."""
        sample_email_calculation_request["email"]["cc"] = ["manager@example.com", "team@example.com"]

        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            response = client.post(
                "/api/v1/email/send-report",
                json=sample_email_calculation_request
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_send_calculation_report_invalid_calculation(self, mock_smtp_settings):
        """Test sending calculation report with invalid calculation data."""
        invalid_request = {
            "calculation": {
                "project": {
                    "project_name": "Test",
                    "created_by": "Test",
                    "creator_email": "test@example.com"
                },
                "camera_groups": [],  # Empty - should fail validation
                "retention_days": 30
            },
            "email": {
                "recipient_email": "customer@example.com",
                "recipient_name": "Jane Smith",
                "include_pdf": True
            }
        }

        response = client.post(
            "/api/v1/email/send-report",
            json=invalid_request
        )

        assert response.status_code == 422  # Validation error

    def test_send_calculation_report_invalid_email(self, mock_smtp_settings, sample_email_calculation_request):
        """Test sending calculation report with invalid email address."""
        sample_email_calculation_request["email"]["recipient_email"] = "invalid-email"

        response = client.post(
            "/api/v1/email/send-report",
            json=sample_email_calculation_request
        )

        assert response.status_code == 422  # Validation error


class TestEmailAPIEdgeCases:
    """Test email API edge cases."""

    def test_send_report_with_special_characters(self, mock_smtp_settings, sample_email_calculation_request):
        """Test sending report with special characters in project name."""
        sample_email_calculation_request["calculation"]["project"]["project_name"] = "Test Project with émojis 🎉"

        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            response = client.post(
                "/api/v1/email/send-report",
                json=sample_email_calculation_request
            )

            assert response.status_code == 200

    def test_send_report_with_long_project_name(self, mock_smtp_settings, sample_email_calculation_request):
        """Test sending report with very long project name."""
        sample_email_calculation_request["calculation"]["project"]["project_name"] = "A" * 500

        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            response = client.post(
                "/api/v1/email/send-report",
                json=sample_email_calculation_request
            )

            assert response.status_code == 200

    def test_send_report_with_multiple_camera_groups(self, mock_smtp_settings, sample_email_calculation_request):
        """Test sending report with multiple camera groups."""
        sample_email_calculation_request["calculation"]["camera_groups"].append({
            "num_cameras": 50,
            "resolution_id": "2mp_1080p",
            "fps": 15,
            "codec_id": "h265",
            "quality": "high",
            "recording_mode": "motion",
            "audio_enabled": True,
            "bitrate_kbps": 2000
        })

        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            response = client.post(
                "/api/v1/email/send-report",
                json=sample_email_calculation_request
            )

            assert response.status_code == 200

    def test_send_report_with_high_retention(self, mock_smtp_settings, sample_email_calculation_request):
        """Test sending report with high retention period."""
        sample_email_calculation_request["calculation"]["retention_days"] = 365

        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            response = client.post(
                "/api/v1/email/send-report",
                json=sample_email_calculation_request
            )

            assert response.status_code == 200

    def test_send_report_with_failover(self, mock_smtp_settings, sample_email_calculation_request):
        """Test sending report with failover configuration."""
        sample_email_calculation_request["calculation"]["server_config"]["failover_type"] = "n_plus_1"

        with patch('app.services.email.sender.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            response = client.post(
                "/api/v1/email/send-report",
                json=sample_email_calculation_request
            )

            assert response.status_code == 200


class TestEmailAPIDocumentation:
    """Test email API documentation."""

    def test_openapi_schema_includes_email_endpoints(self):
        """Test that OpenAPI schema includes email endpoints."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        paths = schema["paths"]

        assert "/api/v1/email/test" in paths
        assert "/api/v1/email/send-report" in paths

    def test_email_test_endpoint_documentation(self):
        """Test email test endpoint has proper documentation."""
        response = client.get("/openapi.json")
        schema = response.json()

        test_endpoint = schema["paths"]["/api/v1/email/test"]["post"]
        assert "summary" in test_endpoint or "description" in test_endpoint

    def test_email_send_report_endpoint_documentation(self):
        """Test email send report endpoint has proper documentation."""
        response = client.get("/openapi.json")
        schema = response.json()

        send_report_endpoint = schema["paths"]["/api/v1/email/send-report"]["post"]
        assert "summary" in send_report_endpoint or "description" in send_report_endpoint

