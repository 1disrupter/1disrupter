# -*- coding: utf-8 -*-
"""Venue ORM model."""
import enum
import uuid

from sqlalchemy import String, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class VenueCategory(str, enum.Enum):
    bar = "bar"
    club = "club"
    live_music = "live_music"


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[VenueCategory] = mapped_column(
        SAEnum(VenueCategory, name="venue_category"), nullable=False
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    vibe = relationship("Vibe", back_populates="venue", uselist=False, cascade="all, delete-orphan")
    feedback = relationship("FeedbackLog", back_populates="venue", cascade="all, delete-orphan")
    external_signals = relationship(
        "VenueSignals", back_populates="venue", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Venue {self.name} ({self.category.value})>"
