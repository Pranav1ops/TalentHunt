import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=True)
    plan = Column(String(50), default="free")  # free, pro, enterprise
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    candidates = relationship("Candidate", back_populates="company", cascade="all, delete-orphan")
    job_descriptions = relationship("JobDescription", back_populates="company", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="company", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="company", uselist=False, cascade="all, delete-orphan")
