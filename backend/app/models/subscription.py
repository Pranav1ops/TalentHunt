import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class PlanType(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    TRIAL = "trial"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, unique=True)
    plan = Column(SAEnum(PlanType), default=PlanType.FREE, nullable=False)
    status = Column(SAEnum(SubscriptionStatus), default=SubscriptionStatus.TRIAL, nullable=False)
    candidate_limit = Column(Integer, default=100)
    jd_limit = Column(Integer, default=10)
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="subscription")
