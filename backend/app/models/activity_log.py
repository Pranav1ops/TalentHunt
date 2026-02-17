import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(255), nullable=False)  # e.g., "created_job", "imported_candidates", "ran_matching"
    resource_type = Column(String(100), nullable=True)  # job, candidate, match
    resource_id = Column(String(255), nullable=True)
    log_metadata = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="activity_logs")
    user = relationship("User", back_populates="activity_logs")
