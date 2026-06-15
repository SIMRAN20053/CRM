from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime
from app.database import Base

class User(Base):
    """Marketer / User of the CRM."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
