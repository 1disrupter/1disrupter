# -*- coding: utf-8 -*-
"""VenueSignals — cached external signals for each venue.

One-to-one with Venue. Refreshed by the background scheduler every 5 minutes.
Kept separate from the existing `vibes` table so the existing score pipeline
remains untouched; the scheduler reads from here and writes the recomputed
score into `vibes`.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class VenueSignals(Base):
    __tablename__ = "venue_signals"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    venue_id: Mapped[str] = mapped_column(
        String, ForeignKey("venues.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )

    google_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    social_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    event_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    time_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    user_votes_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    venue = relationship("Venue", back_populates="external_signals")

    def as_dict(self) -> dict:
        return {
            "google_score": self.google_score,
            "social_score": self.social_score,
            "event_score": self.event_score,
            "time_score": self.time_score,
            "user_votes_score": self.user_votes_score,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
