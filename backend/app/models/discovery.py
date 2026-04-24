# -*- coding: utf-8 -*-
"""Discovery candidate store (new / closed / trending venues).

Admins must approve before these become live venues — no auto-insert.
"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class VenueDiscoveryCandidate(Base):
    __tablename__ = "venue_discovery_candidates"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # new|closed|trending
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reason: Mapped[str] = mapped_column(String(500), default="")
    source: Mapped[str] = mapped_column(String(40), default="heuristic")
    extra: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)  # pending|approved|rejected
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True
    )
