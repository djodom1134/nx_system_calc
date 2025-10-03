"""Webhook API endpoints."""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import datetime

from app.schemas.webhook import (
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
    WebhookListResponse,
    WebhookDeliveryListResponse,
    WebhookTestRequest,
    WebhookTestResponse,
    WebhookEvent,
    WebhookStatus,
)
from app.services.webhook import WebhookService
from app.core.config import get_settings

router = APIRouter()


def check_webhooks_enabled():
    """Dependency to check if webhooks are enabled."""
    settings = get_settings()
    if not settings.enable_webhooks:
        raise HTTPException(
            status_code=403,
            detail="Webhooks are not enabled. Set ENABLE_WEBHOOKS=true in environment."
        )


@router.post("/webhooks", response_model=WebhookResponse, dependencies=[Depends(check_webhooks_enabled)])
async def create_webhook(webhook: WebhookCreate):
    """
    Create a new webhook subscription.
    
    Webhooks allow you to receive real-time notifications when events occur
    in the Nx System Calculator. You can subscribe to specific events and
    receive HTTP POST requests to your specified URL.
    
    **Security:**
    - Provide a secret to enable HMAC signature verification
    - Signature is sent in X-Webhook-Signature header as sha256=<signature>
    - Verify the signature by computing HMAC-SHA256 of the request body
    """
    try:
        result = WebhookService.create_webhook(
            url=str(webhook.url),
            events=[e.value for e in webhook.events],
            secret=webhook.secret,
            description=webhook.description,
            active=webhook.active
        )
        
        return WebhookResponse(
            id=result["id"],
            url=result["url"],
            events=result["events"],
            description=result["description"],
            active=result["active"],
            created_at=result["created_at"],
            updated_at=result["updated_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/webhooks", response_model=WebhookListResponse, dependencies=[Depends(check_webhooks_enabled)])
async def list_webhooks(
    active_only: bool = Query(False, description="Only return active webhooks")
):
    """
    List all webhook subscriptions.
    
    Returns a list of all configured webhooks, optionally filtered to only
    show active webhooks.
    """
    webhooks = WebhookService.list_webhooks(active_only=active_only)
    
    return WebhookListResponse(
        webhooks=[
            WebhookResponse(
                id=w["id"],
                url=w["url"],
                events=w["events"],
                description=w["description"],
                active=w["active"],
                created_at=w["created_at"],
                updated_at=w["updated_at"]
            )
            for w in webhooks
        ],
        total=len(webhooks)
    )


@router.get("/webhooks/{webhook_id}", response_model=WebhookResponse, dependencies=[Depends(check_webhooks_enabled)])
async def get_webhook(webhook_id: str):
    """
    Get a specific webhook subscription by ID.
    """
    webhook = WebhookService.get_webhook(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return WebhookResponse(
        id=webhook["id"],
        url=webhook["url"],
        events=webhook["events"],
        description=webhook["description"],
        active=webhook["active"],
        created_at=webhook["created_at"],
        updated_at=webhook["updated_at"]
    )


@router.patch("/webhooks/{webhook_id}", response_model=WebhookResponse, dependencies=[Depends(check_webhooks_enabled)])
async def update_webhook(webhook_id: str, updates: WebhookUpdate):
    """
    Update a webhook subscription.
    
    You can update the URL, events, secret, description, or active status.
    Only provide the fields you want to update.
    """
    update_data = updates.model_dump(exclude_unset=True)
    
    # Convert URL to string if provided
    if "url" in update_data and update_data["url"]:
        update_data["url"] = str(update_data["url"])
    
    # Convert events to list of strings if provided
    if "events" in update_data and update_data["events"]:
        update_data["events"] = [e.value for e in update_data["events"]]
    
    result = WebhookService.update_webhook(webhook_id, **update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return WebhookResponse(
        id=result["id"],
        url=result["url"],
        events=result["events"],
        description=result["description"],
        active=result["active"],
        created_at=result["created_at"],
        updated_at=result["updated_at"]
    )


@router.delete("/webhooks/{webhook_id}", dependencies=[Depends(check_webhooks_enabled)])
async def delete_webhook(webhook_id: str):
    """
    Delete a webhook subscription.
    
    This will permanently remove the webhook and stop all future deliveries.
    """
    success = WebhookService.delete_webhook(webhook_id)
    if not success:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return {"success": True, "message": "Webhook deleted successfully"}


@router.post("/webhooks/{webhook_id}/test", response_model=WebhookTestResponse, dependencies=[Depends(check_webhooks_enabled)])
async def test_webhook(webhook_id: str, test_request: WebhookTestRequest):
    """
    Test a webhook by sending a sample event.
    
    This sends a test payload to your webhook URL to verify it's working correctly.
    The test payload will include sample data for the specified event type.
    """
    webhook = WebhookService.get_webhook(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    # Create test data based on event type
    test_data = {
        "test": True,
        "event_type": test_request.event.value,
        "timestamp": datetime.utcnow().isoformat(),
        "sample_data": {
            "calculation_id": "test_calc_123",
            "project_name": "Test Project",
            "total_devices": 100,
            "total_storage_tb": 1.5
        }
    }
    
    result = await WebhookService.deliver_webhook(
        webhook_id=webhook_id,
        event=test_request.event,
        data=test_data
    )
    
    return WebhookTestResponse(
        success=result.get("success", False),
        status_code=result.get("status_code"),
        response_body=result.get("response_body"),
        error_message=result.get("error")
    )


@router.get("/webhooks/{webhook_id}/deliveries", response_model=WebhookDeliveryListResponse, dependencies=[Depends(check_webhooks_enabled)])
async def list_webhook_deliveries(
    webhook_id: str,
    status: Optional[WebhookStatus] = Query(None, description="Filter by delivery status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of deliveries to return")
):
    """
    List delivery attempts for a specific webhook.
    
    Returns a history of all delivery attempts, including successful deliveries,
    failures, and retries. Useful for debugging webhook issues.
    """
    webhook = WebhookService.get_webhook(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    deliveries = WebhookService.list_deliveries(
        webhook_id=webhook_id,
        status=status,
        limit=limit
    )
    
    from app.schemas.webhook import WebhookDelivery
    
    return WebhookDeliveryListResponse(
        deliveries=[
            WebhookDelivery(
                id=d["id"],
                webhook_id=d["webhook_id"],
                event=d["event"],
                status=d["status"],
                attempt=d["attempt"],
                max_attempts=d["max_attempts"],
                response_code=d["response_code"],
                response_body=d["response_body"],
                error_message=d["error_message"],
                created_at=d["created_at"],
                delivered_at=d["delivered_at"],
                next_retry_at=d["next_retry_at"]
            )
            for d in deliveries
        ],
        total=len(deliveries)
    )


@router.get("/webhook-events", dependencies=[Depends(check_webhooks_enabled)])
async def list_webhook_events():
    """
    List all available webhook event types.
    
    Returns a list of all events you can subscribe to, with descriptions.
    """
    events = [
        {
            "event": WebhookEvent.CALCULATION_COMPLETED.value,
            "description": "Triggered when a calculation completes successfully"
        },
        {
            "event": WebhookEvent.CALCULATION_FAILED.value,
            "description": "Triggered when a calculation fails"
        },
        {
            "event": WebhookEvent.MULTI_SITE_COMPLETED.value,
            "description": "Triggered when a multi-site calculation completes successfully"
        },
        {
            "event": WebhookEvent.MULTI_SITE_FAILED.value,
            "description": "Triggered when a multi-site calculation fails"
        },
        {
            "event": WebhookEvent.PDF_GENERATED.value,
            "description": "Triggered when a PDF report is generated successfully"
        },
        {
            "event": WebhookEvent.PDF_FAILED.value,
            "description": "Triggered when PDF generation fails"
        }
    ]
    
    return {"events": events}

