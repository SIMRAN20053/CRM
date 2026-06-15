from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime

class CustomerCreate(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None
    total_spend: Optional[float] = 0.0
    visit_count: Optional[int] = 0
    last_purchase_at: Optional[datetime] = None
    segment_tags: Optional[str] = None
    metadata_json: Optional[str] = None

class CustomerUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    total_spend: Optional[float] = None
    visit_count: Optional[int] = None
    last_purchase_at: Optional[datetime] = None
    segment_tags: Optional[str] = None
    metadata_json: Optional[str] = None

class CustomerResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: Optional[str] = None
    total_spend: float
    visit_count: int
    last_purchase_at: Optional[datetime] = None
    segment_tags: Optional[str] = None
    metadata_json: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CustomerListResponse(BaseModel):
    customers: List[CustomerResponse]
    total: int
    page: int
    page_size: int

class CustomerBulkCreate(BaseModel):
    customers: List[CustomerCreate]

from app.schemas.order import OrderResponse

class CustomerDetailResponse(BaseModel):
    customer: CustomerResponse
    orders: List[OrderResponse]

