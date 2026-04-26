"""WhatsApp webhook endpoint."""
from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from config import logger, settings

router = APIRouter()


class WhatsAppMessage(BaseModel):
    """WhatsApp message schema."""
    from_number: str
    message: str
    timestamp: str


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    WhatsApp webhook endpoint for receiving messages from Twilio.

    This is a placeholder implementation. In production, this would:
    1. Verify Twilio request signature
    2. Parse WhatsApp message from Twilio format
    3. Process with chat endpoint
    4. Send response back via Twilio

    Args:
        request: Webhook request

    Returns:
        Success response
    """
    try:
        if not settings.enable_whatsapp:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="WhatsApp integration not enabled"
            )

        # Get form data from Twilio
        form_data = await request.form()

        from_number = form_data.get("From", "")
        message_body = form_data.get("Body", "")

        logger.info(f"WhatsApp message from {from_number}: {message_body[:100]}...")

        # TODO: Implement full WhatsApp integration
        # 1. Verify signature
        # 2. Map phone number to customer_id
        # 3. Call chat endpoint
        # 4. Send response via Twilio API

        return {
            "status": "received",
            "message": "WhatsApp integration coming soon"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/whatsapp")
async def whatsapp_webhook_verify(request: Request):
    """
    Webhook verification endpoint for WhatsApp.

    Args:
        request: Verification request

    Returns:
        Challenge response
    """
    # Twilio verification (example)
    return {"status": "webhook_verified"}
