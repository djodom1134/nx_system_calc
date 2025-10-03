"""Tests for webhook functionality."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.services.webhook import WebhookService
from app.schemas.webhook import WebhookEvent, WebhookStatus

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


class TestWebhookAPI:
    """Test webhook API endpoints."""
    
    def test_create_webhook(self, enable_webhooks):
        """Test creating a webhook."""
        response = client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://example.com/webhook",
                "events": ["calculation.completed"],
                "secret": "test-secret",
                "description": "Test webhook"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["url"] == "https://example.com/webhook"
        assert "calculation.completed" in data["events"]
        assert data["description"] == "Test webhook"
        assert data["active"] is True
        assert "id" in data
        assert data["id"].startswith("wh_")
    
    def test_create_webhook_disabled(self):
        """Test creating webhook when webhooks are disabled."""
        response = client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://example.com/webhook",
                "events": ["calculation.completed"]
            }
        )
        
        assert response.status_code == 403
        assert "not enabled" in response.json()["detail"]
    
    def test_list_webhooks(self, enable_webhooks):
        """Test listing webhooks."""
        # Create some webhooks
        client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://example.com/webhook1",
                "events": ["calculation.completed"]
            }
        )
        client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://example.com/webhook2",
                "events": ["pdf.generated"],
                "active": False
            }
        )
        
        # List all webhooks
        response = client.get("/api/v1/webhooks")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["webhooks"]) == 2
        
        # List only active webhooks
        response = client.get("/api/v1/webhooks?active_only=true")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
    
    def test_get_webhook(self, enable_webhooks):
        """Test getting a specific webhook."""
        # Create webhook
        create_response = client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://example.com/webhook",
                "events": ["calculation.completed"]
            }
        )
        webhook_id = create_response.json()["id"]
        
        # Get webhook
        response = client.get(f"/api/v1/webhooks/{webhook_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == webhook_id
        assert data["url"] == "https://example.com/webhook"
    
    def test_get_webhook_not_found(self, enable_webhooks):
        """Test getting non-existent webhook."""
        response = client.get("/api/v1/webhooks/wh_nonexistent")
        assert response.status_code == 404
    
    def test_update_webhook(self, enable_webhooks):
        """Test updating a webhook."""
        # Create webhook
        create_response = client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://example.com/webhook",
                "events": ["calculation.completed"]
            }
        )
        webhook_id = create_response.json()["id"]
        
        # Update webhook
        response = client.patch(
            f"/api/v1/webhooks/{webhook_id}",
            json={
                "url": "https://example.com/new-webhook",
                "active": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["url"] == "https://example.com/new-webhook"
        assert data["active"] is False
    
    def test_delete_webhook(self, enable_webhooks):
        """Test deleting a webhook."""
        # Create webhook
        create_response = client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://example.com/webhook",
                "events": ["calculation.completed"]
            }
        )
        webhook_id = create_response.json()["id"]
        
        # Delete webhook
        response = client.delete(f"/api/v1/webhooks/{webhook_id}")
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Verify deleted
        response = client.get(f"/api/v1/webhooks/{webhook_id}")
        assert response.status_code == 404
    
    def test_list_webhook_events(self, enable_webhooks):
        """Test listing available webhook events."""
        response = client.get("/api/v1/webhook-events")
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert len(data["events"]) > 0
        
        # Check for expected events
        event_types = [e["event"] for e in data["events"]]
        assert "calculation.completed" in event_types
        assert "pdf.generated" in event_types


class TestWebhookService:
    """Test webhook service functionality."""
    
    def test_create_webhook_service(self):
        """Test creating webhook via service."""
        webhook = WebhookService.create_webhook(
            url="https://example.com/webhook",
            events=["calculation.completed"],
            secret="test-secret"
        )
        
        assert webhook["id"].startswith("wh_")
        assert webhook["url"] == "https://example.com/webhook"
        assert webhook["events"] == ["calculation.completed"]
        assert webhook["secret"] == "test-secret"
        assert webhook["active"] is True
    
    def test_list_webhooks_service(self):
        """Test listing webhooks via service."""
        WebhookService.create_webhook(
            url="https://example.com/webhook1",
            events=["calculation.completed"],
            active=True
        )
        WebhookService.create_webhook(
            url="https://example.com/webhook2",
            events=["pdf.generated"],
            active=False
        )
        
        # List all
        all_webhooks = WebhookService.list_webhooks()
        assert len(all_webhooks) == 2
        
        # List active only
        active_webhooks = WebhookService.list_webhooks(active_only=True)
        assert len(active_webhooks) == 1
    
    @pytest.mark.asyncio
    async def test_deliver_webhook_success(self):
        """Test successful webhook delivery."""
        webhook = WebhookService.create_webhook(
            url="https://example.com/webhook",
            events=["calculation.completed"]
        )
        
        # Mock HTTP client
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = '{"status": "ok"}'
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            result = await WebhookService.deliver_webhook(
                webhook_id=webhook["id"],
                event=WebhookEvent.CALCULATION_COMPLETED,
                data={"test": "data"}
            )
            
            assert result["success"] is True
            assert result["status_code"] == 200
    
    @pytest.mark.asyncio
    async def test_deliver_webhook_failure(self):
        """Test failed webhook delivery."""
        webhook = WebhookService.create_webhook(
            url="https://example.com/webhook",
            events=["calculation.completed"]
        )
        
        # Mock HTTP client with failure
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            result = await WebhookService.deliver_webhook(
                webhook_id=webhook["id"],
                event=WebhookEvent.CALCULATION_COMPLETED,
                data={"test": "data"}
            )
            
            assert result["success"] is False
            assert result["status_code"] == 500
    
    @pytest.mark.asyncio
    async def test_trigger_event(self):
        """Test triggering event for multiple webhooks."""
        # Create multiple webhooks
        WebhookService.create_webhook(
            url="https://example.com/webhook1",
            events=["calculation.completed"]
        )
        WebhookService.create_webhook(
            url="https://example.com/webhook2",
            events=["calculation.completed", "pdf.generated"]
        )
        WebhookService.create_webhook(
            url="https://example.com/webhook3",
            events=["pdf.generated"]  # Different event
        )
        
        # Mock HTTP client
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = '{"status": "ok"}'
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            results = await WebhookService.trigger_event(
                event=WebhookEvent.CALCULATION_COMPLETED,
                data={"test": "data"}
            )
            
            # Should trigger 2 webhooks (webhook1 and webhook2)
            assert len(results) == 2

