# -*- coding: utf-8 -*-
"""WebhookEventLog — DB-backed durable log of outbound webhook dispatches."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Index, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WebhookEventLog(Base):
    __tablename__ = "webhook_event_log"
    __table_args__ = (
        Index("ix_webhook_event_log_type", "event_type"),
        Index("ix_webhook_event_log_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    meta: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    ok: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    error: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    attempts: Mapped[int] = mapped_column(String(8), nullable=False, default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc),
    )

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "event_type": self.event_type,
            "title": self.title,
            "body": self.body,
            "meta": self.meta or {},
            "ok": self.ok,
            "error": self.error,
            "ts": self.created_at.timestamp() if self.created_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
