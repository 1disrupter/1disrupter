# -*- coding: utf-8 -*-
"""Push notification tokens (additive) — maps an opaque wallet_id to an Expo push token."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserPushToken(Base):
    __tablename__ = "user_push_tokens"

    # wallet_id is the opaque client-supplied user_id (same one used by /rewards/*)
    wallet_id: Mapped[str] = mapped_column(String, primary_key=True)
    expo_push_token: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
