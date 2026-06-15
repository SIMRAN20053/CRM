import json
import logging
import asyncio
import random
from datetime import datetime
from uuid import uuid4
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.campaign import Campaign
from app.models.segment import Segment
from app.models.communication_log import CommunicationLog
from app.services.segment_engine import segment_engine
from app.services.channel_client import channel_client

logger = logging.getLogger(__name__)

async def simulate_campaign_delivery(campaign_id: str):
    """Simulates delivery, open, read, and click rates in the background."""
    logger.info(f"Starting background campaign delivery simulation for {campaign_id}")
    
    # 1. Wait a bit for the frontend to register that it's launching
    await asyncio.sleep(3)
    
    async with async_session() as session:
        try:
            # Fetch campaign
            result = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
            campaign = result.scalar_one_or_none()
            if not campaign:
                logger.error(f"Campaign {campaign_id} not found for simulation")
                return
            
            # Fetch all communication logs
            log_result = await session.execute(
                select(CommunicationLog).where(CommunicationLog.campaign_id == campaign_id)
            )
            logs = log_result.scalars().all()
            if not logs:
                logger.error(f"No logs found for campaign {campaign_id} to simulate")
                return
            
            total = len(logs)
            campaign.status = "active"
            
            # Phase 1: Sent & Delivered / Failed (Simulate 95% delivery)
            delivered_count = 0
            failed_count = 0
            for log in logs:
                # Randomize order slightly
                if random.random() < 0.95:
                    log.status = "delivered"
                    log.delivered_at = datetime.utcnow()
                    delivered_count += 1
                else:
                    log.status = "failed"
                    log.failed_at = datetime.utcnow()
                    log.failure_reason = "Delivery failed by channel gateway"
                    failed_count += 1
            
            campaign.total_sent = total
            campaign.delivered = delivered_count
            campaign.failed = failed_count
            await session.commit()
            logger.info(f"Campaign {campaign_id} - Phase 1: Sent and delivered/failed updated")
            
            # Wait for user to observe the active state and delivered metrics
            await asyncio.sleep(4)
            
            # Refresh logs to get current status
            log_result = await session.execute(
                select(CommunicationLog).where(CommunicationLog.campaign_id == campaign_id)
            )
            logs = log_result.scalars().all()
            
            # Phase 2: Opened & Read (Simulate 60% open rate, 80% of open get read)
            opened_count = 0
            read_count = 0
            for log in logs:
                if log.status == "delivered":
                    if random.random() < 0.60:
                        log.status = "opened"
                        log.opened_at = datetime.utcnow()
                        opened_count += 1
                        
                        if random.random() < 0.80:
                            log.status = "read"
                            log.read_at = datetime.utcnow()
                            read_count += 1
            
            campaign.opened = opened_count
            campaign.read = read_count
            await session.commit()
            logger.info(f"Campaign {campaign_id} - Phase 2: Opened/read updated")
            
            # Wait before simulating click outcomes
            await asyncio.sleep(4)
            
            # Refresh logs again
            log_result = await session.execute(
                select(CommunicationLog).where(CommunicationLog.campaign_id == campaign_id)
            )
            logs = log_result.scalars().all()
            
            # Phase 3: Clicked (Simulate 18% click rate of opened/read)
            clicked_count = 0
            for log in logs:
                if log.status in ("opened", "read"):
                    if random.random() < 0.18:
                        log.status = "clicked"
                        log.clicked_at = datetime.utcnow()
                        clicked_count += 1
            
            campaign.clicked = clicked_count
            campaign.status = "completed"
            campaign.completed_at = datetime.utcnow()
            await session.commit()
            logger.info(f"Campaign {campaign_id} - Phase 3: Completed simulation")
            
        except Exception as e:
            logger.error(f"Error in campaign delivery simulation for {campaign_id}: {e}", exc_info=True)

class CampaignEngine:
    """Orchestrates campaign launch, delivery tracking, and metrics aggregation."""
    
    async def launch_campaign(self, campaign: Campaign, db: AsyncSession) -> dict:
        """Launch a campaign: resolve audience, create logs, invoke channel client, trigger simulation."""
        if campaign.status not in ("draft", "failed"):
            raise ValueError(f"Campaign cannot be launched from status '{campaign.status}'")
        
        # 1. Update status to launching
        campaign.status = "launching"
        campaign.launched_at = datetime.utcnow()
        await db.commit()
        await db.refresh(campaign)
        
        # 2. Fetch segment and audience
        result = await db.execute(select(Segment).where(Segment.id == campaign.segment_id))
        segment = result.scalar_one_or_none()
        if not segment:
            campaign.status = "failed"
            await db.commit()
            raise ValueError(f"Segment {campaign.segment_id} not found")
        
        rules = json.loads(segment.rules) if isinstance(segment.rules, str) else segment.rules
        audience = await segment_engine.get_audience(rules, db)
        
        if not audience:
            campaign.status = "failed"
            await db.commit()
            raise ValueError("No customers matched this campaign's audience segment")
        
        # 3. Create communication logs for each customer
        comm_logs = []
        messages_to_send = []
        
        for customer in audience:
            # Personalize message template
            message = campaign.message_template.replace("{{name}}", customer.name)
            
            log = CommunicationLog(
                id=str(uuid4()),
                campaign_id=campaign.id,
                customer_id=customer.id,
                channel=campaign.channel,
                message=message,
                status="pending",
                sent_at=datetime.utcnow()
            )
            comm_logs.append(log)
            messages_to_send.append({
                "log_id": log.id,
                "customer_id": customer.id,
                "customer_name": customer.name,
                "customer_email": customer.email,
                "customer_phone": customer.phone,
                "channel": campaign.channel,
                "message": message,
            })
        
        db.add_all(comm_logs)
        await db.flush()
        
        # 4. Attempt to send messages to the external stubbed channel service
        sent_to_gateway = await channel_client.send_messages(messages_to_send)
        if sent_to_gateway:
            logger.info(f"Successfully sent {len(messages_to_send)} messages to external channel service.")
        else:
            logger.warning("External channel service not responding or returned error. Falling back to local simulation.")
        
        # Update campaign total count and status to active
        campaign.status = "active"
        campaign.total_sent = len(audience)
        await db.commit()
        await db.refresh(campaign)
        
        # 5. Fire background task to simulate real-time updates of delivered/opened/read/clicked statuses
        asyncio.create_task(simulate_campaign_delivery(campaign.id))
        
        return {
            "status": "launched",
            "campaign_id": campaign.id,
            "audience_size": len(audience),
            "message": "Campaign launched successfully. Delivery simulation running in background."
        }
    
    async def get_campaign_stats(self, campaign_id: str, db: AsyncSession) -> dict:
        """Get aggregate campaign metrics from the campaign record directly (which gets updated live)."""
        result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
        campaign = result.scalar_one_or_none()
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        total_sent = campaign.total_sent
        delivered = campaign.delivered
        failed = campaign.failed
        opened = campaign.opened
        read = campaign.read
        clicked = campaign.clicked
        
        return {
            "total_sent": total_sent,
            "delivered": delivered,
            "failed": failed,
            "opened": opened,
            "read": read,
            "clicked": clicked,
            "delivery_rate": (delivered / total_sent * 100) if total_sent > 0 else 0.0,
            "open_rate": (opened / delivered * 100) if delivered > 0 else 0.0,
            "click_rate": (clicked / delivered * 100) if delivered > 0 else 0.0,
        }

    async def process_receipt(
        self,
        log_id: str,
        status: str,
        timestamp: str | None,
        reason: str | None,
        db: AsyncSession,
    ) -> None:
        """Process a delivery/engagement receipt for a communication log."""
        log_result = await db.execute(select(CommunicationLog).where(CommunicationLog.id == log_id))
        log = log_result.scalar_one_or_none()
        if not log:
            logger.warning(f"Communication log {log_id} not found for receipt status {status}")
            return
        
        if log.status == status:
            return
            
        log.status = status
        
        t_val = datetime.utcnow()
        if timestamp:
            try:
                t_val = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except Exception:
                pass
                
        if status == "sent":
            log.sent_at = t_val
        elif status == "delivered":
            log.delivered_at = t_val
        elif status == "failed":
            log.failed_at = t_val
            log.failure_reason = reason
        elif status == "opened":
            log.opened_at = t_val
        elif status == "read":
            log.read_at = t_val
        elif status == "clicked":
            log.clicked_at = t_val
            
        db.add(log)
        await db.flush()
        
        # Update campaign aggregates
        campaign_id = log.campaign_id
        campaign_result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
        campaign = campaign_result.scalar_one_or_none()
        
        if campaign:
            sent_res = await db.execute(
                select(func.count(CommunicationLog.id)).where(CommunicationLog.campaign_id == campaign_id)
            )
            campaign.total_sent = sent_res.scalar() or 0
            
            del_res = await db.execute(
                select(func.count(CommunicationLog.id)).where(
                    CommunicationLog.campaign_id == campaign_id,
                    CommunicationLog.status.in_(["delivered", "opened", "read", "clicked"])
                )
            )
            campaign.delivered = del_res.scalar() or 0
            
            fail_res = await db.execute(
                select(func.count(CommunicationLog.id)).where(
                    CommunicationLog.campaign_id == campaign_id,
                    CommunicationLog.status == "failed"
                )
            )
            campaign.failed = fail_res.scalar() or 0
            
            open_res = await db.execute(
                select(func.count(CommunicationLog.id)).where(
                    CommunicationLog.campaign_id == campaign_id,
                    CommunicationLog.status.in_(["opened", "read", "clicked"])
                )
            )
            campaign.opened = open_res.scalar() or 0
            
            read_res = await db.execute(
                select(func.count(CommunicationLog.id)).where(
                    CommunicationLog.campaign_id == campaign_id,
                    CommunicationLog.status.in_(["read", "clicked"])
                )
            )
            campaign.read = read_res.scalar() or 0
            
            click_res = await db.execute(
                select(func.count(CommunicationLog.id)).where(
                    CommunicationLog.campaign_id == campaign_id,
                    CommunicationLog.status == "clicked"
                )
            )
            campaign.clicked = click_res.scalar() or 0
            
            db.add(campaign)
            await db.flush()

# Singleton
campaign_engine = CampaignEngine()
