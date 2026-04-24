# -*- coding: utf-8 -*-
"""VenueClaim model — owners verifying control of a venue."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, JSON, String, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class VenueClaim(Base):
    __tablename__ = "venue_claims"
    __table_args__ = (
        Index("ix_venue_claims_venue_id", "venue_id"),
        Index("ix_venue_claims_email", "email"),
        Index("ix_venue_claims_status", "status"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    venue_id: Mapped[str] = mapped_column(String, ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    owner_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    proof: Mapped[str] = mapped_column(String(500), default="")
    # pending | email_sent | verified | rejected
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    # Magic-link token fields. Token is single-use + time-limited.
    token: Mapped[Optional[str]] = mapped_column(String(80), nullable=True, unique=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    meta: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc),
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewer: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "venue_id": self.venue_id,
            "owner_name": self.owner_name,
            "email": self.email,
            "proof": self.proof,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "reviewer": self.reviewer,
            "meta": self.meta or {},
        }
