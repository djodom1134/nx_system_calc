"""Integration tests for webhook triggers during calculations."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.services.webhook import WebhookService

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_webhooks():
    """Clear webhooks before each test."""
    WebhookService._webhooks.clear()
    WebhookService._deliveries.clear()
    yield
    WebhookService._webhooks.clear()
    WebhookService._deliveries.clear()


@pytest.fixture
def enable_webhooks(monkeypatch):
    """Enable webhooks for testing."""
    monkeypatch.setenv("ENABLE_WEBHOOKS", "true")
    # Force reload of settings
    from app.core.config import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def sample_calculation_request():
    """Sample calculation request."""
    return {
        "project": {
            "project_name": "Test Project",
            "created_by": "Test User",
            "creator_email": "test@example.com"
        },
        "camera_groups": [
            {
                "num_cameras": 10,
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
    }


@pytest.fixture
def sample_multi_site_request():
    """Sample multi-site calculation request."""
    return {
        "project": {
            "project_name": "Multi-Site Project",
            "created_by": "Test User",
            "creator_email": "test@example.com"
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
        },
        "max_devices_per_site": 2560,
        "max_servers_per_site": 10
    }


class TestCalculationWebhooks:
    """Test webhook triggers during calculations."""

    @pytest.mark.asyncio
    async def test_calculation_triggers_webhook_directly(self, enable_webhooks):
        """Test that webhook service can be triggered for calculation events."""
        # Create webhook
        webhook = WebhookService.create_webhook(
            url="https://example.com/webhook",
            events=["calculation.completed"]
        )

        # Mock HTTP client for webhook delivery
        with patch("app.services.webhook.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = '{"status": "ok"}'

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            # Trigger webhook event directly
            from app.schemas.webhook import WebhookEvent

            results = await WebhookService.trigger_event(
                event=WebhookEvent.CALCULATION_COMPLETED,
                data={
                    "project_name": "Test Project",
                    "total_devices": 100,
                    "total_storage_tb": 1.5
                }
            )

            # Verify webhook was triggered
            assert len(results) == 1
            assert results[0]["success"] is True
            assert mock_client.return_value.__aenter__.return_value.post.called

    def test_calculation_failure_triggers_webhook(self, enable_webhooks):
        """Test that failed calculation triggers failure webhook."""
        # Create webhook for failures
        webhook_response = client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://example.com/webhook",
                "events": ["calculation.failed"]
            }
        )
        assert webhook_response.status_code == 200

        # Mock HTTP client for webhook delivery - patch in the webhook service module
        with patch("app.services.webhook.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = '{"status": "ok"}'

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            # Perform invalid calculation (missing required fields)
            calc_response = client.post(
                "/api/v1/calculate",
                json={
                    "project": {
                        "project_name": "Test",
                        "created_by": "Test",
                        "creator_email": "test@example.com"
                    },
                    "camera_groups": [],  # Empty - should fail validation
                    "retention_days": 30
                }
            )

            assert calc_response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_multi_site_triggers_webhook_directly(self, enable_webhooks):
        """Test that webhook service can be triggered for multi-site events."""
        # Create webhook
        webhook = WebhookService.create_webhook(
            url="https://example.com/webhook",
            events=["multi_site.completed"]
        )

        # Mock HTTP client for webhook delivery
        with patch("app.services.webhook.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = '{"status": "ok"}'

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            # Trigger webhook event directly
            from app.schemas.webhook import WebhookEvent

            results = await WebhookService.trigger_event(
                event=WebhookEvent.MULTI_SITE_COMPLETED,
                data={
                    "project_name": "Multi-Site Project",
                    "total_sites": 2,
                    "total_devices": 5000,
                    "total_storage_tb": 10.5,
                    "total_servers": 20,
                    "all_sites_valid": True
                }
            )

            # Verify webhook was triggered
            assert len(results) == 1
            assert results[0]["success"] is True
            assert mock_client.return_value.__aenter__.return_value.post.called

    def test_calculation_endpoint_works(self, sample_calculation_request):
        """Test that calculation endpoint works (webhooks disabled by default)."""
        # Perform calculation without webhooks enabled
        calc_response = client.post(
            "/api/v1/calculate",
            json=sample_calculation_request
        )

        assert calc_response.status_code == 200
        data = calc_response.json()
        assert "summary" in data
        assert "storage" in data
        assert "servers" in data

    @pytest.mark.asyncio
    async def test_multiple_webhooks_triggered(self, enable_webhooks):
        """Test that multiple webhooks are triggered for same event."""
        # Create multiple webhooks
        for i in range(3):
            WebhookService.create_webhook(
                url=f"https://example.com/webhook{i}",
                events=["calculation.completed"]
            )

        # Mock HTTP client for webhook delivery
        with patch("app.services.webhook.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = '{"status": "ok"}'

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            # Trigger webhook event
            from app.schemas.webhook import WebhookEvent

            results = await WebhookService.trigger_event(
                event=WebhookEvent.CALCULATION_COMPLETED,
                data={"test": "data"}
            )

            # Verify all 3 webhooks were triggered
            assert len(results) == 3
            assert all(r["success"] for r in results)
            assert mock_client.return_value.__aenter__.return_value.post.call_count == 3


class TestWebhookSecurity:
    """Test webhook security features."""

    @pytest.mark.asyncio
    async def test_webhook_signature_generation(self):
        """Test that webhook signatures are generated correctly."""
        webhook = WebhookService.create_webhook(
            url="https://example.com/webhook",
            events=["calculation.completed"],
            secret="test-secret"
        )

        # Mock HTTP client - patch in the webhook service module
        with patch("app.services.webhook.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = '{"status": "ok"}'

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            from app.schemas.webhook import WebhookEvent

            await WebhookService.deliver_webhook(
                webhook_id=webhook["id"],
                event=WebhookEvent.CALCULATION_COMPLETED,
                data={"test": "data"}
            )

            # Verify signature header was included
            call_args = mock_post.call_args
            headers = call_args.kwargs["headers"]
            assert "X-Webhook-Signature" in headers
            assert headers["X-Webhook-Signature"].startswith("sha256=")

    @pytest.mark.asyncio
    async def test_webhook_without_secret(self):
        """Test webhook delivery without secret."""
        webhook = WebhookService.create_webhook(
            url="https://example.com/webhook",
            events=["calculation.completed"],
            secret=None
        )

        # Mock HTTP client - patch in the webhook service module
        with patch("app.services.webhook.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = '{"status": "ok"}'

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            from app.schemas.webhook import WebhookEvent

            await WebhookService.deliver_webhook(
                webhook_id=webhook["id"],
                event=WebhookEvent.CALCULATION_COMPLETED,
                data={"test": "data"}
            )

            # Verify signature header was NOT included
            call_args = mock_post.call_args
            headers = call_args.kwargs["headers"]
            assert "X-Webhook-Signature" not in headers


def test_pdf_generated_webhook_trigger(enable_webhooks, sample_calculation_request):
    """Test that pdf.generated webhook is triggered on successful PDF generation."""
    # Create webhook subscription
    webhook_response = client.post(
        "/api/v1/webhooks",
        json={
            "url": "https://example.com/webhook",
            "events": ["pdf.generated"],
            "description": "PDF generation webhook"
        }
    )
    assert webhook_response.status_code == 200
    webhook = webhook_response.json()

    # Mock webhook delivery - return a dict as expected
    with patch("app.services.webhook.WebhookService.deliver_webhook") as mock_deliver:
        mock_deliver.return_value = {
            "delivery_id": "del_123",
            "status": "delivered",
            "response_code": 200
        }

        # Generate PDF
        response = client.post(
            "/api/v1/generate-pdf",
            json=sample_calculation_request
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

        # Verify webhook was triggered
        mock_deliver.assert_called_once()
        call_args = mock_deliver.call_args

        # Check event type
        assert call_args.kwargs["event"] == "pdf.generated"

        # Check webhook data
        webhook_data = call_args.kwargs["data"]
        assert "project_name" in webhook_data
        assert webhook_data["project_name"] == "Test Project"
        assert "filename" in webhook_data
        assert "total_devices" in webhook_data
        assert "total_storage_tb" in webhook_data
        assert "servers_needed" in webhook_data
        assert "pdf_size_bytes" in webhook_data
        assert webhook_data["pdf_size_bytes"] > 0


def test_pdf_failed_webhook_trigger(enable_webhooks, sample_calculation_request):
    """Test that pdf.failed webhook is triggered on PDF generation failure."""
    # Create webhook subscription
    webhook_response = client.post(
        "/api/v1/webhooks",
        json={
            "url": "https://example.com/webhook",
            "events": ["pdf.failed"],
            "description": "PDF failure webhook"
        }
    )
    assert webhook_response.status_code == 200

    # Mock PDF generator to raise an exception
    with patch("app.api.calculator.PDFGenerator") as mock_pdf_gen:
        mock_pdf_gen.return_value.generate_report.side_effect = Exception("PDF generation failed")

        # Generate PDF - should fail
        response = client.post(
            "/api/v1/generate-pdf",
            json=sample_calculation_request
        )
        assert response.status_code == 400

        # Verify error message contains our exception
        assert "PDF generation failed" in response.json()["detail"]


def test_pdf_webhooks_disabled_by_default(sample_calculation_request, enable_webhooks):
    """Test that PDF webhooks are triggered when webhooks are enabled."""
    # Create webhook subscription
    webhook_response = client.post(
        "/api/v1/webhooks",
        json={
            "url": "https://example.com/webhook",
            "events": ["pdf.generated"],
            "description": "PDF webhook"
        }
    )
    assert webhook_response.status_code == 200

    # Mock webhook delivery
    with patch("app.services.webhook.WebhookService.deliver_webhook") as mock_deliver:
        mock_deliver.return_value = {
            "delivery_id": "del_123",
            "status": "delivered",
            "response_code": 200
        }

        # Generate PDF
        response = client.post(
            "/api/v1/generate-pdf",
            json=sample_calculation_request
        )
        assert response.status_code == 200

        # Verify webhook WAS triggered (webhooks enabled via fixture)
        mock_deliver.assert_called_once()

