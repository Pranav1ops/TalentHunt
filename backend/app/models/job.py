import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    raw_text = Column(Text, nullable=False)
    parsed_data = Column(JSON, nullable=True)
    # parsed_data structure:
    # {
    #   "skills": {"mandatory": [...], "optional": [...]},
    #   "seniority": "senior",
    #   "experience_range": {"min": 5, "max": 10},
    #   "tools": [...],
    #   "industry": "fintech",
    #   "location": "Remote",
    #   "salary_band": {"min": 100000, "max": 150000, "currency": "USD"},
    #   "domain": "backend"
    # }
    embedding = Column(JSON, nullable=True)
    status = Column(String(50), default="active")  # active, closed, draft
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="job_descriptions")
    creator = relationship("User", foreign_keys=[created_by])
    matches = relationship("Match", back_populates="job_description", cascade="all, delete-orphan")
