from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class OrderCreate(BaseModel):
    customer_id: str
    amount: float
    status: Optional[str] = "completed"
    items: Optional[str] = None  # JSON string of items in order
    order_date: datetime = datetime.utcnow()

class OrderResponse(BaseModel):
    id: str
    customer_id: str
    amount: float
    status: str
    items: Optional[str] = None
    order_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int

class OrderBulkCreate(BaseModel):
    orders: List[OrderCreate]
