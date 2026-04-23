# -*- coding: utf-8 -*-
"""Vibe ORM model — one row per venue storing the score & raw signals."""
import enum
from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CrowdLevel(str, enum.Enum):
    busy = "busy"
    medium = "medium"
    dead = "dead"


class Vibe(Base):
    __tablename__ = "vibes"

    venue_id: Mapped[str] = mapped_column(
        String, ForeignKey("venues.id", ondelete="CASCADE"), primary_key=True
    )
    vibe_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    crowd_level: Mapped[CrowdLevel] = mapped_column(
        SAEnum(CrowdLevel, name="crowd_level"), nullable=False, default=CrowdLevel.dead
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Raw signals
    manual_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    social_activity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    user_votes: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    time_prediction: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    venue_boost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    venue = relationship("Venue", back_populates="vibe")

    def signals_dict(self) -> dict:
        return {
            "manual_score": self.manual_score,
            "social_activity": self.social_activity,
            "user_votes": self.user_votes,
            "time_prediction": self.time_prediction,
            "venue_boost": self.venue_boost,
        }
