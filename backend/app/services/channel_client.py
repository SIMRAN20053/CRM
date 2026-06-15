import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class ChannelClient:
    """Client for communicating with the external stubbed Channel Service."""
    
    def __init__(self):
        self.base_url = settings.CHANNEL_SERVICE_URL
        
    async def send_messages(self, messages: list[dict]) -> bool:
        """Send a batch of messages to the Channel Service for delivery simulation.
        
        Each message dict contains:
            - log_id: ID of the communication log
            - customer_id: Customer ID
            - customer_name: Name of the customer
            - customer_email: Email
            - customer_phone: Phone
            - channel: whatsapp / sms / email / rcs
            - message: Personalised message content
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/send-batch",
                    json={"messages": messages}
                )
                if response.status_code in (200, 201, 202):
                    return True
                logger.error(f"Channel service responded with code {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.warning(f"Could not connect to Channel Service at {self.base_url}: {e}. Local mock simulation will be used.")
            return False

channel_client = ChannelClient()
