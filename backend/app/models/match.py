import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class Match(Base):
    __tablename__ = "matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    overall_score = Column(Float, default=0)
    confidence = Column(Float, default=0)
    skill_score = Column(Float, default=0)
    experience_score = Column(Float, default=0)
    seniority_score = Column(Float, default=0)
    location_score = Column(Float, default=0)
    compensation_score = Column(Float, default=0)
    recency_score = Column(Float, default=0)
    domain_score = Column(Float, default=0)
    availability_score = Column(Float, default=0)
    strengths = Column(JSON, default=list)   # list of strength descriptions
    weaknesses = Column(JSON, default=list)  # list of weakness/gap descriptions
    explanation = Column(JSON, default=dict)  # detailed AI explanation per dimension
    created_at = Column(DateTime, default=datetime.utcnow)

    job_description = relationship("JobDescription", back_populates="matches")
    candidate = relationship("Candidate", back_populates="matches")
    rediscovery_signals = relationship("RediscoverySignal", back_populates="match", cascade="all, delete-orphan")


class SignalType(str, enum.Enum):
    PREVIOUSLY_REJECTED_SIMILAR = "previously_rejected_similar"
    SKILLS_NOW_TRENDING = "skills_now_trending"
    NOW_AVAILABLE = "now_available"
    LONG_INACTIVE_STRONG_MATCH = "long_inactive_strong_match"
    NEAR_MISS = "near_miss"
    RECENT_UPSKILLING = "recent_upskilling"
    SIMILAR_ROLE_HISTORY = "similar_role_history"


class RediscoverySignal(Base):
    __tablename__ = "rediscovery_signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    signal_type = Column(SAEnum(SignalType), nullable=False)
    reason = Column(String(1000), nullable=False)
    score_boost = Column(Float, default=0)
    signal_metadata = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("Match", back_populates="rediscovery_signals")
    candidate = relationship("Candidate", back_populates="rediscovery_signals")
