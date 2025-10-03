"""Webhook schemas and models."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class WebhookEvent(str, Enum):
    """Webhook event types."""
    
    CALCULATION_COMPLETED = "calculation.completed"
    CALCULATION_FAILED = "calculation.failed"
    MULTI_SITE_COMPLETED = "multi_site.completed"
    MULTI_SITE_FAILED = "multi_site.failed"
    PDF_GENERATED = "pdf.generated"
    PDF_FAILED = "pdf.failed"


class WebhookStatus(str, Enum):
    """Webhook delivery status."""
    
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class WebhookCreate(BaseModel):
    """Create webhook subscription."""
    
    url: HttpUrl = Field(..., description="Webhook callback URL")
    events: List[WebhookEvent] = Field(..., min_length=1, description="Events to subscribe to")
    secret: Optional[str] = Field(None, description="Secret for signature verification")
    description: Optional[str] = Field(None, max_length=500, description="Webhook description")
    active: bool = Field(default=True, description="Whether webhook is active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/webhooks/nx-calculator",
                "events": ["calculation.completed", "pdf.generated"],
                "secret": "your-secret-key",
                "description": "Production webhook for calculation results",
                "active": True
            }
        }


class WebhookUpdate(BaseModel):
    """Update webhook subscription."""
    
    url: Optional[HttpUrl] = None
    events: Optional[List[WebhookEvent]] = None
    secret: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class WebhookResponse(BaseModel):
    """Webhook subscription response."""
    
    id: str = Field(..., description="Webhook ID")
    url: str = Field(..., description="Webhook callback URL")
    events: List[str] = Field(..., description="Subscribed events")
    description: Optional[str] = None
    active: bool = Field(..., description="Whether webhook is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "wh_1234567890",
                "url": "https://example.com/webhooks/nx-calculator",
                "events": ["calculation.completed", "pdf.generated"],
                "description": "Production webhook",
                "active": True,
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:30:00Z"
            }
        }


class WebhookPayload(BaseModel):
    """Webhook event payload."""
    
    event: WebhookEvent = Field(..., description="Event type")
    webhook_id: str = Field(..., description="Webhook ID")
    timestamp: datetime = Field(..., description="Event timestamp")
    data: Dict[str, Any] = Field(..., description="Event data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event": "calculation.completed",
                "webhook_id": "wh_1234567890",
                "timestamp": "2025-01-15T10:30:00Z",
                "data": {
                    "calculation_id": "calc_abc123",
                    "project_name": "Test Project",
                    "total_devices": 100,
                    "total_storage_tb": 1.5
                }
            }
        }


class WebhookDelivery(BaseModel):
    """Webhook delivery attempt."""
    
    id: str = Field(..., description="Delivery ID")
    webhook_id: str = Field(..., description="Webhook ID")
    event: str = Field(..., description="Event type")
    status: WebhookStatus = Field(..., description="Delivery status")
    attempt: int = Field(..., description="Attempt number")
    max_attempts: int = Field(default=3, description="Maximum retry attempts")
    response_code: Optional[int] = Field(None, description="HTTP response code")
    response_body: Optional[str] = Field(None, description="Response body")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Creation timestamp")
    delivered_at: Optional[datetime] = Field(None, description="Delivery timestamp")
    next_retry_at: Optional[datetime] = Field(None, description="Next retry timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "del_1234567890",
                "webhook_id": "wh_1234567890",
                "event": "calculation.completed",
                "status": "delivered",
                "attempt": 1,
                "max_attempts": 3,
                "response_code": 200,
                "response_body": '{"status": "ok"}',
                "error_message": None,
                "created_at": "2025-01-15T10:30:00Z",
                "delivered_at": "2025-01-15T10:30:01Z",
                "next_retry_at": None
            }
        }


class WebhookListResponse(BaseModel):
    """List of webhooks."""
    
    webhooks: List[WebhookResponse]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "webhooks": [
                    {
                        "id": "wh_1234567890",
                        "url": "https://example.com/webhooks/nx-calculator",
                        "events": ["calculation.completed"],
                        "description": "Production webhook",
                        "active": True,
                        "created_at": "2025-01-15T10:30:00Z",
                        "updated_at": "2025-01-15T10:30:00Z"
                    }
                ],
                "total": 1
            }
        }


class WebhookDeliveryListResponse(BaseModel):
    """List of webhook deliveries."""
    
    deliveries: List[WebhookDelivery]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "deliveries": [
                    {
                        "id": "del_1234567890",
                        "webhook_id": "wh_1234567890",
                        "event": "calculation.completed",
                        "status": "delivered",
                        "attempt": 1,
                        "max_attempts": 3,
                        "response_code": 200,
                        "created_at": "2025-01-15T10:30:00Z",
                        "delivered_at": "2025-01-15T10:30:01Z"
                    }
                ],
                "total": 1
            }
        }


class WebhookTestRequest(BaseModel):
    """Test webhook request."""
    
    event: WebhookEvent = Field(..., description="Event type to test")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event": "calculation.completed"
            }
        }


class WebhookTestResponse(BaseModel):
    """Test webhook response."""
    
    success: bool
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "status_code": 200,
                "response_body": '{"status": "ok"}',
                "error_message": None
            }
        }

