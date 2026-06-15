from pydantic import BaseModel, ConfigDict, model_validator
from typing import Optional, List, Any, Union
from datetime import datetime
import json

class SegmentRule(BaseModel):
    field: str
    operator: str
    value: Any  # Can be integer, float, string, etc.

class SegmentRules(BaseModel):
    conditions: List[SegmentRule]
    logic: str = "AND"  # AND / OR

class SegmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rules: SegmentRules
    ai_reasoning: Optional[str] = None
    confidence_score: Optional[float] = None

class SegmentResponse(BaseModel):
    id: str
    created_by: Optional[str] = None
    name: str
    description: Optional[str] = None
    rules: SegmentRules
    ai_reasoning: Optional[str] = None
    confidence_score: Optional[float] = None
    audience_size: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def parse_rules(cls, data: Any) -> Any:
        if hasattr(data, "rules"):
            # It's a SQLAlchemy model instance
            rules_val = getattr(data, "rules")
            data_dict = {}
            for col in data.__table__.columns:
                data_dict[col.name] = getattr(data, col.name)
            
            if isinstance(rules_val, str):
                try:
                    data_dict["rules"] = json.loads(rules_val)
                except Exception:
                    data_dict["rules"] = {"conditions": [], "logic": "AND"}
            else:
                data_dict["rules"] = rules_val or {"conditions": [], "logic": "AND"}
            return data_dict
            
        elif isinstance(data, dict):
            # It's a dictionary
            rules_val = data.get("rules")
            if isinstance(rules_val, str):
                try:
                    data["rules"] = json.loads(rules_val)
                except Exception:
                    data["rules"] = {"conditions": [], "logic": "AND"}
            elif "rules" not in data:
                data["rules"] = {"conditions": [], "logic": "AND"}
            return data
            
        return data

class SegmentListResponse(BaseModel):
    segments: List[SegmentResponse]
    total: int
