from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Float, Integer, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Customer(Base):
    """Customer database record."""
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    total_spend = Column(Float, default=0.0)
    visit_count = Column(Integer, default=0)
    last_purchase_at = Column(DateTime, nullable=True)
    segment_tags = Column(String(500), nullable=True)  # Comma-separated tags
    metadata_json = Column(Text, nullable=True)  # JSON string for flexible attributes
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    communication_logs = relationship("CommunicationLog", back_populates="customer", cascade="all, delete-orphan")
