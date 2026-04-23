# -*- coding: utf-8 -*-
"""Feedback audit log — every submitted vote is persisted."""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class VoteType(str, enum.Enum):
    busy = "busy"
    dead = "dead"
    good = "good"


class FeedbackLog(Base):
    __tablename__ = "feedback_log"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    venue_id: Mapped[str] = mapped_column(
        String, ForeignKey("venues.id", ondelete="CASCADE"), nullable=False, index=True
    )
    vote: Mapped[VoteType] = mapped_column(SAEnum(VoteType, name="vote_type"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    venue = relationship("Venue", back_populates="feedback")
