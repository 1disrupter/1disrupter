# -*- coding: utf-8 -*-
"""Launch-mode + intelligence models (additive).

- `VenueIntel`  — persisted tourist/gem classifier output per venue
- `NotificationLog` — fire-and-forget ledger for the mobile push inbox
- `VenueProfile` — city-launch metadata (hours, music, price, dress-code…)
- `VenueAdmin`  — per-venue login credentials (hash, not plain text)
"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class VenueIntel(Base):
    __tablename__ = "venue_intel"
    venue_id: Mapped[str] = mapped_column(String, ForeignKey("venues.id", ondelete="CASCADE"), primary_key=True)
    label: Mapped[str] = mapped_column(String(20), nullable=False, default="neutral")
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reason: Mapped[str] = mapped_column(String(500), default="")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class NotificationLog(Base):
    __tablename__ = "notification_log"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    wallet_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(String(500), nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True
    )


class VenueProfile(Base):
    __tablename__ = "venue_profiles"
    venue_id: Mapped[str] = mapped_column(String, ForeignKey("venues.id", ondelete="CASCADE"), primary_key=True)
    opening_hours: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)   # {"mon":"20:00-02:00",...}
    music_type: Mapped[str] = mapped_column(String(80), default="")
    price_level: Mapped[int] = mapped_column(Integer, default=2)                     # 1-4 ($-$$$$)
    age_group: Mapped[str] = mapped_column(String(40), default="")                   # e.g. "21+"
    dress_code: Mapped[str] = mapped_column(String(80), default="")
    photos: Mapped[list] = mapped_column(JSON, nullable=False, default=list)         # list of URLs
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class VenueAdmin(Base):
    __tablename__ = "venue_admins"
    username: Mapped[str] = mapped_column(String(120), primary_key=True)
    venue_id: Mapped[str] = mapped_column(String, ForeignKey("venues.id", ondelete="CASCADE"), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    api_key: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
