"""Webhook delivery service."""

import hashlib
import hmac
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import httpx
import asyncio

from app.schemas.webhook import (
    WebhookEvent,
    WebhookStatus,
    WebhookPayload,
    WebhookDelivery,
)


class WebhookService:
    """Service for managing and delivering webhooks."""
    
    # In-memory storage (replace with database in production)
    _webhooks: Dict[str, Dict[str, Any]] = {}
    _deliveries: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def create_webhook(
        cls,
        url: str,
        events: List[str],
        secret: Optional[str] = None,
        description: Optional[str] = None,
        active: bool = True
    ) -> Dict[str, Any]:
        """Create a new webhook subscription."""
        webhook_id = f"wh_{uuid.uuid4().hex[:16]}"
        now = datetime.utcnow()
        
        webhook = {
            "id": webhook_id,
            "url": url,
            "events": events,
            "secret": secret,
            "description": description,
            "active": active,
            "created_at": now,
            "updated_at": now,
        }
        
        cls._webhooks[webhook_id] = webhook
        return webhook
    
    @classmethod
    def get_webhook(cls, webhook_id: str) -> Optional[Dict[str, Any]]:
        """Get webhook by ID."""
        return cls._webhooks.get(webhook_id)
    
    @classmethod
    def list_webhooks(cls, active_only: bool = False) -> List[Dict[str, Any]]:
        """List all webhooks."""
        webhooks = list(cls._webhooks.values())
        if active_only:
            webhooks = [w for w in webhooks if w["active"]]
        return webhooks
    
    @classmethod
    def update_webhook(
        cls,
        webhook_id: str,
        **updates
    ) -> Optional[Dict[str, Any]]:
        """Update webhook subscription."""
        webhook = cls._webhooks.get(webhook_id)
        if not webhook:
            return None
        
        webhook.update(updates)
        webhook["updated_at"] = datetime.utcnow()
        return webhook
    
    @classmethod
    def delete_webhook(cls, webhook_id: str) -> bool:
        """Delete webhook subscription."""
        if webhook_id in cls._webhooks:
            del cls._webhooks[webhook_id]
            return True
        return False
    
    @classmethod
    def _generate_signature(cls, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload."""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    @classmethod
    async def deliver_webhook(
        cls,
        webhook_id: str,
        event: WebhookEvent,
        data: Dict[str, Any],
        attempt: int = 1,
        max_attempts: int = 3
    ) -> Dict[str, Any]:
        """Deliver webhook to endpoint."""
        webhook = cls.get_webhook(webhook_id)
        if not webhook or not webhook["active"]:
            return {
                "success": False,
                "error": "Webhook not found or inactive"
            }
        
        # Create delivery record
        delivery_id = f"del_{uuid.uuid4().hex[:16]}"
        now = datetime.utcnow()
        
        delivery = {
            "id": delivery_id,
            "webhook_id": webhook_id,
            "event": event.value,
            "status": WebhookStatus.PENDING.value,
            "attempt": attempt,
            "max_attempts": max_attempts,
            "response_code": None,
            "response_body": None,
            "error_message": None,
            "created_at": now,
            "delivered_at": None,
            "next_retry_at": None,
        }
        
        cls._deliveries[delivery_id] = delivery
        
        # Build payload
        payload = WebhookPayload(
            event=event,
            webhook_id=webhook_id,
            timestamp=now,
            data=data
        )
        
        payload_json = payload.model_dump_json()
        
        # Generate signature if secret is provided
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Nx-System-Calculator-Webhook/1.0",
            "X-Webhook-Event": event.value,
            "X-Webhook-ID": webhook_id,
            "X-Webhook-Delivery": delivery_id,
        }
        
        if webhook["secret"]:
            signature = cls._generate_signature(payload_json, webhook["secret"])
            headers["X-Webhook-Signature"] = f"sha256={signature}"
        
        # Attempt delivery
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    webhook["url"],
                    content=payload_json,
                    headers=headers
                )
                
                delivery["response_code"] = response.status_code
                delivery["response_body"] = response.text[:1000]  # Limit size
                
                if 200 <= response.status_code < 300:
                    delivery["status"] = WebhookStatus.DELIVERED.value
                    delivery["delivered_at"] = datetime.utcnow()
                    return {
                        "success": True,
                        "delivery_id": delivery_id,
                        "status_code": response.status_code
                    }
                else:
                    delivery["status"] = WebhookStatus.FAILED.value
                    delivery["error_message"] = f"HTTP {response.status_code}"
                    
                    # Schedule retry if attempts remaining
                    if attempt < max_attempts:
                        delivery["status"] = WebhookStatus.RETRYING.value
                        # Exponential backoff: 1min, 5min, 15min
                        retry_delay = min(60 * (5 ** (attempt - 1)), 900)
                        delivery["next_retry_at"] = now + timedelta(seconds=retry_delay)
                    
                    return {
                        "success": False,
                        "delivery_id": delivery_id,
                        "status_code": response.status_code,
                        "error": delivery["error_message"]
                    }
                    
        except Exception as e:
            delivery["status"] = WebhookStatus.FAILED.value
            delivery["error_message"] = str(e)
            
            # Schedule retry if attempts remaining
            if attempt < max_attempts:
                delivery["status"] = WebhookStatus.RETRYING.value
                retry_delay = min(60 * (5 ** (attempt - 1)), 900)
                delivery["next_retry_at"] = now + timedelta(seconds=retry_delay)
            
            return {
                "success": False,
                "delivery_id": delivery_id,
                "error": str(e)
            }
    
    @classmethod
    async def trigger_event(
        cls,
        event: WebhookEvent,
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Trigger webhook event for all subscribed webhooks."""
        results = []
        
        # Find all active webhooks subscribed to this event
        for webhook in cls.list_webhooks(active_only=True):
            if event.value in webhook["events"]:
                result = await cls.deliver_webhook(
                    webhook_id=webhook["id"],
                    event=event,
                    data=data
                )
                results.append({
                    "webhook_id": webhook["id"],
                    **result
                })
        
        return results
    
    @classmethod
    def get_delivery(cls, delivery_id: str) -> Optional[Dict[str, Any]]:
        """Get delivery by ID."""
        return cls._deliveries.get(delivery_id)
    
    @classmethod
    def list_deliveries(
        cls,
        webhook_id: Optional[str] = None,
        status: Optional[WebhookStatus] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List webhook deliveries."""
        deliveries = list(cls._deliveries.values())
        
        if webhook_id:
            deliveries = [d for d in deliveries if d["webhook_id"] == webhook_id]
        
        if status:
            deliveries = [d for d in deliveries if d["status"] == status.value]
        
        # Sort by created_at descending
        deliveries.sort(key=lambda x: x["created_at"], reverse=True)
        
        return deliveries[:limit]
    
    @classmethod
    async def retry_failed_deliveries(cls) -> List[Dict[str, Any]]:
        """Retry failed webhook deliveries that are due for retry."""
        now = datetime.utcnow()
        results = []
        
        for delivery in cls._deliveries.values():
            if (delivery["status"] == WebhookStatus.RETRYING.value and
                delivery["next_retry_at"] and
                delivery["next_retry_at"] <= now):
                
                webhook_id = delivery["webhook_id"]
                event = WebhookEvent(delivery["event"])
                
                # Get original data from delivery (simplified - in production, store separately)
                result = await cls.deliver_webhook(
                    webhook_id=webhook_id,
                    event=event,
                    data={},  # Would need to store original data
                    attempt=delivery["attempt"] + 1,
                    max_attempts=delivery["max_attempts"]
                )
                
                results.append({
                    "delivery_id": delivery["id"],
                    **result
                })
        
        return results

