# -*- coding: utf-8 -*-
"""Wallet operations — opaque `user_id` -> credit balance."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import UserWallet


def get_wallet(db: Session, user_id: str) -> UserWallet:
    w = db.get(UserWallet, user_id)
    if w is None:
        w = UserWallet(user_id=user_id, credits=0)
        db.add(w)
        db.commit()
        db.refresh(w)
    return w


def add_credits(db: Session, user_id: str, amount: int) -> UserWallet:
    if amount <= 0:
        raise ValueError("amount must be > 0")
    w = get_wallet(db, user_id)
    w.credits = int(w.credits or 0) + int(amount)
    w.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(w)
    return w


def deduct_credits(db: Session, user_id: str, amount: int) -> UserWallet:
    if amount <= 0:
        raise ValueError("amount must be > 0")
    w = get_wallet(db, user_id)
    if (w.credits or 0) < amount:
        raise ValueError("insufficient credits")
    w.credits = int(w.credits) - int(amount)
    w.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(w)
    return w
