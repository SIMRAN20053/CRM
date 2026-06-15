"""AI endpoints — the hero of SmartReach AI.

Provides natural-language objective → campaign plan generation
and post-campaign insight analysis.
"""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.campaign import Campaign
from app.models.customer import Customer
from app.schemas.ai import (
    AIPlanResponse,
    AIInsightsResponse,
    ObjectiveRequest,
)
from app.services.ai_engine import ai_engine
from app.services.campaign_engine import campaign_engine
from app.services.segment_engine import segment_engine

router = APIRouter(prefix="/api/ai", tags=["ai"])


async def _get_customer_stats(db: AsyncSession) -> dict:
    """Gather aggregate customer statistics for the AI context."""
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)

    # Total count
    total_result = await db.execute(select(func.count(Customer.id)))
    total_count = total_result.scalar() or 0

    # Average spend
    avg_spend_result = await db.execute(
        select(func.avg(Customer.total_spend))
    )
    avg_spend = round(float(avg_spend_result.scalar() or 0), 2)

    # Average visits
    avg_visits_result = await db.execute(
        select(func.avg(Customer.visit_count))
    )
    avg_visits = round(float(avg_visits_result.scalar() or 0), 2)

    # Recent active (purchased within last 30 days)
    recent_active_result = await db.execute(
        select(func.count(Customer.id)).where(
            Customer.last_purchase_at >= thirty_days_ago
        )
    )
    recent_active = recent_active_result.scalar() or 0

    # Inactive (no purchase in last 60 days)
    inactive_result = await db.execute(
        select(func.count(Customer.id)).where(
            Customer.last_purchase_at < sixty_days_ago
        )
    )
    inactive_count = inactive_result.scalar() or 0

    # High-value (total_spend > 15000)
    high_value_result = await db.execute(
        select(func.count(Customer.id)).where(Customer.total_spend > 15000)
    )
    high_value_count = high_value_result.scalar() or 0

    return {
        "total_customers": total_count,
        "avg_spend": avg_spend,
        "avg_visits": avg_visits,
        "recent_active_count": recent_active,
        "inactive_count": inactive_count,
        "high_value_count": high_value_count,
    }


@router.post("/objective", response_model=AIPlanResponse)
async def generate_campaign_plan(
    request: ObjectiveRequest, db: AsyncSession = Depends(get_db)
):
    """Convert a natural-language marketing objective into an actionable campaign plan.

    Steps:
    1. Gather customer statistics from the database.
    2. Ask the AI engine to produce segment rules and a message template.
    3. Use the segment engine to calculate actual audience size.
    4. Return the full plan.
    """
    stats = await _get_customer_stats(db)

    plan = await ai_engine.generate_campaign_plan(request.objective, stats)

    # Calculate real audience size from the generated rules
    audience_size = 0
    if plan.get("rules"):
        audience_size = await segment_engine.calculate_audience_size(
            plan["rules"], db
        )

    # Extract recommended channel
    rec_channel = "whatsapp"
    if isinstance(plan.get("channel_recommendation"), dict):
        rec_channel = plan["channel_recommendation"].get("channel", "whatsapp")
    elif isinstance(plan.get("channel_recommendation"), str):
        rec_channel = plan["channel_recommendation"]

    # Extract message template based on recommended channel
    messages = plan.get("messages", {})
    message_template = ""
    if isinstance(messages, dict):
        if rec_channel == "email":
            subject = messages.get("email_subject", "")
            body = messages.get("email_body", "")
            message_template = f"Subject: {subject}\n\n{body}" if subject else body
        else:
            message_template = messages.get(rec_channel, "")
        
        # Fallback to any non-empty message template in dict
        if not message_template:
            for val in messages.values():
                if val and isinstance(val, str):
                    message_template = val
                    break
    
    if not message_template:
        message_template = plan.get("message_template", "")

    # Extract reasoning
    reasoning = plan.get("audience_reasoning") or plan.get("reasoning") or ""
    if isinstance(plan.get("channel_recommendation"), dict):
        chan_reasoning = plan["channel_recommendation"].get("reasoning")
        if chan_reasoning:
            reasoning = f"{reasoning}\n\nChannel Recommendation ({rec_channel}): {chan_reasoning}".strip()

    return AIPlanResponse(
        objective=request.objective,
        segment_name=plan.get("segment_name", "AI Generated Segment"),
        rules=plan.get("rules", []),
        message_template=message_template,
        audience_size=audience_size,
        reasoning=reasoning,
        customer_stats=stats,
        channel=rec_channel,
    )


@router.post("/insights/{campaign_id}", response_model=AIInsightsResponse)
async def generate_campaign_insights(
    campaign_id: str, db: AsyncSession = Depends(get_db)
):
    """Generate AI-powered insights for a completed campaign."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Fetch delivery stats
    stats = await campaign_engine.get_campaign_stats(campaign_id, db)

    campaign_data = {
        "id": str(campaign.id),
        "name": campaign.name,
        "status": campaign.status,
        "message_template": campaign.message_template,
        "created_at": str(campaign.created_at),
        "stats": stats,
    }

    insights = await ai_engine.generate_insights(campaign_data)

    findings = insights.get("key_findings", [])
    insights_str = "\n".join([f"- {f}" for f in findings]) if isinstance(findings, list) else insights.get("insights", "")
    if not insights_str and isinstance(findings, str):
        insights_str = findings

    perf_summary = insights.get("summary") or insights.get("performance_summary") or ""

    return AIInsightsResponse(
        campaign_id=campaign_id,
        campaign_name=campaign.name,
        insights=insights_str,
        recommendations=insights.get("recommendations", []),
        performance_summary=perf_summary,
    )
