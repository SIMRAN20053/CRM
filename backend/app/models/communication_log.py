from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class CommunicationLog(Base):
    """Log tracking individual message deliveries and customer interactions."""
    __tablename__ = "communication_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    channel = Column(String(50), nullable=False)  # whatsapp, sms, email, rcs
    message = Column(Text, nullable=False)
    status = Column(String(50), default="pending")  # pending, sent, delivered, failed, opened, read, clicked
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    failure_reason = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    campaign = relationship("Campaign", back_populates="communication_logs")
    customer = relationship("Customer", back_populates="communication_logs")
