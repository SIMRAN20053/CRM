from pydantic import BaseModel
from typing import Optional, List, Any, Union

class ObjectiveRequest(BaseModel):
    objective: str

class AIPlanResponse(BaseModel):
    objective: str
    segment_name: str
    rules: Any  # Can be list, dict, or SegmentRules depending on fallback/LLM output
    message_template: str
    audience_size: int
    reasoning: str
    customer_stats: dict
    channel: Optional[str] = "whatsapp"

class AIInsightsRequest(BaseModel):
    campaign_id: str

class AIInsightsResponse(BaseModel):
    campaign_id: str
    campaign_name: str
    insights: str
    recommendations: List[str]
    performance_summary: str
