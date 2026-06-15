"""Campaign endpoints — CRUD, launch, stats, and communication logs."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.campaign import Campaign
from app.models.communication_log import CommunicationLog
from app.schemas.campaign import (
    CampaignCreate,
    CampaignListResponse,
    CampaignResponse,
)
from app.services.campaign_engine import campaign_engine

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(db: AsyncSession = Depends(get_db)):
    """List all campaigns ordered by creation date (newest first)."""
    total_result = await db.execute(select(func.count(Campaign.id)))
    total = total_result.scalar() or 0
    
    result = await db.execute(
        select(Campaign).order_by(Campaign.created_at.desc())
    )
    campaigns = result.scalars().all()
    return CampaignListResponse(
        campaigns=[CampaignResponse.model_validate(c) for c in campaigns],
        total=total,
    )


@router.post("", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    payload: CampaignCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new campaign with status='draft'."""
    campaign = Campaign(
        name=payload.name,
        segment_id=payload.segment_id,
        objective=payload.objective,
        channel=payload.channel,
        message_template=payload.message_template,
        ai_reasoning=payload.ai_reasoning,
        channel_confidence=payload.channel_confidence,
        predicted_open_rate=payload.predicted_open_rate,
        predicted_click_rate=payload.predicted_click_rate,
        predicted_engagement_score=payload.predicted_engagement_score,
        status="draft",
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return CampaignResponse.model_validate(campaign)


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single campaign's details."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignResponse.model_validate(campaign)


@router.post("/{campaign_id}/launch")
async def launch_campaign(campaign_id: str, db: AsyncSession = Depends(get_db)):
    """Launch a campaign — sends messages to the segment audience."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.status not in ("draft", "failed"):
        raise HTTPException(
            status_code=400,
            detail=f"Campaign cannot be launched from status '{campaign.status}'",
        )

    try:
        launch_result = await campaign_engine.launch_campaign(campaign, db)
        return launch_result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{campaign_id}/stats")
async def get_campaign_stats(
    campaign_id: str, db: AsyncSession = Depends(get_db)
):
    """Get delivery / engagement stats for a campaign."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    stats = await campaign_engine.get_campaign_stats(campaign_id, db)
    return stats


@router.get("/{campaign_id}/logs")
async def get_campaign_logs(
    campaign_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated communication logs for a campaign."""
    offset = (page - 1) * page_size

    total_result = await db.execute(
        select(func.count(CommunicationLog.id)).where(
            CommunicationLog.campaign_id == campaign_id
        )
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        select(CommunicationLog)
        .where(CommunicationLog.campaign_id == campaign_id)
        .order_by(CommunicationLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    logs = result.scalars().all()

    return {
        "campaign_id": campaign_id,
        "total": total,
        "page": page,
        "page_size": page_size,
        "logs": [
            {
                "id": str(log.id),
                "customer_id": str(log.customer_id),
                "status": log.status,
                "message": log.message,
                "sent_at": str(log.sent_at) if log.sent_at else None,
                "delivered_at": str(log.delivered_at) if log.delivered_at else None,
                "failed_at": str(log.failed_at) if log.failed_at else None,
                "failure_reason": log.failure_reason,
                "created_at": str(log.created_at),
            }
            for log in logs
        ],
    }
