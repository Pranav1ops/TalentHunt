import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    skills = Column(JSON, default=list)  # list of skill strings
    experience_years = Column(Float, default=0)
    current_status = Column(String(50), default="available")  # available, unavailable, employed, open_to_offers
    last_interaction = Column(DateTime, nullable=True)
    previous_submissions = Column(JSON, default=list)  # list of {job_title, date, outcome}
    availability = Column(String(100), default="immediate")
    salary_expectation = Column(Float, nullable=True)  # in LPA or USD
    salary_currency = Column(String(10), default="USD")
    location = Column(String(255), nullable=True)
    open_to_remote = Column(String(10), default="false")
    notes = Column(Text, nullable=True)
    resume_text = Column(Text, nullable=True)
    embedding = Column(JSON, nullable=True)  # stored TF-IDF vector
    seniority = Column(String(50), nullable=True)  # junior, mid, senior, lead, principal
    industry = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="candidates")
    matches = relationship("Match", back_populates="candidate", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="candidate", cascade="all, delete-orphan")
    rediscovery_signals = relationship("RediscoverySignal", back_populates="candidate", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=True)  # programming, framework, database, cloud, etc.
    is_trending = Column(String(10), default="false")
    created_at = Column(DateTime, default=datetime.utcnow)
