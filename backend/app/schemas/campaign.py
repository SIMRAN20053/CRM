from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class CampaignCreate(BaseModel):
    segment_id: str
    name: str
    objective: Optional[str] = None
    channel: str  # whatsapp, sms, email, rcs
    message_template: str
    ai_reasoning: Optional[str] = None
    channel_confidence: Optional[float] = None
    predicted_open_rate: Optional[float] = None
    predicted_click_rate: Optional[float] = None
    predicted_engagement_score: Optional[float] = None

class CampaignResponse(BaseModel):
    id: str
    segment_id: str
    created_by: Optional[str] = None
    name: str
    objective: Optional[str] = None
    channel: str
    message_template: str
    status: str
    ai_reasoning: Optional[str] = None
    ai_suggestions_json: Optional[str] = None
    channel_confidence: Optional[float] = None
    predicted_open_rate: Optional[float] = None
    predicted_click_rate: Optional[float] = None
    predicted_engagement_score: Optional[float] = None

    # Outcome stats
    total_sent: int
    delivered: int
    failed: int
    opened: int
    read: int
    clicked: int

    launched_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CampaignListResponse(BaseModel):
    campaigns: List[CampaignResponse]
    total: int

class CampaignStats(BaseModel):
    total_sent: int
    delivered: int
    failed: int
    opened: int
    read: int
    clicked: int
    delivery_rate: float  # (delivered / total_sent) * 100
    open_rate: float      # (opened / delivered) * 100
    click_rate: float     # (clicked / delivered) * 100
