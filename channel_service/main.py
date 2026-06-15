import asyncio
import logging
import random
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("channel_service")

app = FastAPI(
    title="SmartReach AI - Stubbed Channel Service",
    description="Simulates asynchronous messaging gateway behaviors (WhatsApp, SMS, Email, RCS) and callback webhooks.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
CRM_WEBHOOK_URL = "http://localhost:8000/api/receipts"

# Schemas
class MessagePayload(BaseModel):
    log_id: str
    customer_id: str
    customer_name: str
    customer_email: str
    customer_phone: str
    channel: str
    message: str

class SendBatchRequest(BaseModel):
    messages: List[MessagePayload]

# Async Webhook Client
async def send_webhook(log_id: str, status: str, reason: Optional[str] = None):
    """Post status updates back to the CRM service."""
    payload = {
        "log_id": log_id,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reason": reason
    }
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(CRM_WEBHOOK_URL, json=payload)
            if response.status_code == 200:
                logger.info(f"Callback SUCCESS: Log {log_id} -> {status}")
            else:
                logger.error(f"Callback FAILED: CRM responded with status {response.status_code} for log {log_id}")
    except Exception as e:
        logger.error(f"Callback ERROR connecting to CRM at {CRM_WEBHOOK_URL} for log {log_id}: {e}")

# Delivery Simulation Task
async def simulate_delivery_lifecycle(message: MessagePayload):
    """Simulates realistic timing delays and event funnel for message statuses."""
    log_id = message.log_id
    channel = message.channel
    
    # 1. Simulate Network Sending Delay (1-3 seconds)
    await asyncio.sleep(random.uniform(1.0, 3.0))
    
    # 2. Sent & Delivery Phase (95% delivered, 5% failed)
    if random.random() < 0.95:
        await send_webhook(log_id, "delivered")
    else:
        reason = random.choice([
            "Invalid recipient address / number format",
            "Recipient carrier network timeout",
            "Message blocked by spam filter",
            "Subscriber phone powered off or out of range"
        ])
        await send_webhook(log_id, "failed", reason=reason)
        return  # End lifecycle for failed deliveries
        
    # 3. Simulate Reading Time Delay (2-5 seconds)
    await asyncio.sleep(random.uniform(2.0, 5.0))
    
    # 4. Open/Read Phase (Funnel progression)
    # Open rate: whatsapp: 80%, email: 40%, sms: 60%, rcs: 70%
    open_rates = {"whatsapp": 0.80, "email": 0.40, "sms": 0.60, "rcs": 0.70}
    open_prob = open_rates.get(channel.lower(), 0.60)
    
    if random.random() < open_prob:
        await send_webhook(log_id, "opened")
        
        # WhatsApp, RCS, and Email show read receipts
        if channel.lower() in ("whatsapp", "rcs", "email"):
            await asyncio.sleep(random.uniform(1.0, 3.0))
            await send_webhook(log_id, "read")
            
        # 5. Click Phase (Simulate click-through rate: 20% of open/read)
        await asyncio.sleep(random.uniform(2.0, 5.0))
        if random.random() < 0.20:
            await send_webhook(log_id, "clicked")

# Endpoints
@app.post("/api/send-batch")
async def send_batch(request: SendBatchRequest, background_tasks: BackgroundTasks):
    """Receive a batch of messages, return success immediately, and trigger background simulation."""
    logger.info(f"Received batch of {len(request.messages)} messages for delivery simulation.")
    
    for message in request.messages:
        background_tasks.add_task(simulate_delivery_lifecycle, message)
        
    return {
        "status": "accepted",
        "batch_size": len(request.messages),
        "message": "Delivery simulation triggered asynchronously."
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Stubbed Channel Service"}

@app.get("/")
async def root():
    return {
        "message": "Welcome to SmartReach AI Channel Service Simulator",
        "documentation": "/docs"
    }
