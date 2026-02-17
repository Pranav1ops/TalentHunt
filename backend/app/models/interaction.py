import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ActionType(str, enum.Enum):
    CONTACTED = "contacted"
    PIPELINED = "pipelined"
    REJECTED = "rejected"
    SAVED = "saved"
    EXPORTED = "exported"
    NOTED = "noted"


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True)
    action = Column(SAEnum(ActionType), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="interactions")
    user = relationship("User", back_populates="interactions")
    job_description = relationship("JobDescription", foreign_keys=[job_id])
