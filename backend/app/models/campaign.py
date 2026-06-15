from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Campaign(Base):
    """Campaign parameters and execution metrics."""
    __tablename__ = "campaigns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    segment_id = Column(String(36), ForeignKey("segments.id"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False)
    objective = Column(Text, nullable=True)
    channel = Column(String(50), nullable=False)  # whatsapp, sms, email, rcs
    message_template = Column(Text, nullable=False)
    status = Column(String(50), default="draft")  # draft, launching, active, completed, failed
    ai_reasoning = Column(Text, nullable=True)
    ai_suggestions_json = Column(Text, nullable=True)  # suggestions stored as JSON
    channel_confidence = Column(Float, nullable=True)
    predicted_open_rate = Column(Float, nullable=True)
    predicted_click_rate = Column(Float, nullable=True)
    predicted_engagement_score = Column(Float, nullable=True)

    # Actual delivery & engagement statistics
    total_sent = Column(Integer, default=0)
    delivered = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    opened = Column(Integer, default=0)
    read = Column(Integer, default=0)
    clicked = Column(Integer, default=0)

    launched_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    segment = relationship("Segment", back_populates="campaigns")
    communication_logs = relationship("CommunicationLog", back_populates="campaign", cascade="all, delete-orphan")
