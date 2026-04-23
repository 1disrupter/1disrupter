# -*- coding: utf-8 -*-
"""Push notification routes (additive)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.notifications import register_token, send_push

router = APIRouter(prefix="/notifications", tags=["notifications"])


class RegisterIn(BaseModel):
    wallet_id: str = Field(..., min_length=1, max_length=120)
    expo_push_token: str = Field(..., min_length=1, max_length=500)


class RegisterOut(BaseModel):
    wallet_id: str
    registered: bool


@router.post("/register", response_model=RegisterOut, summary="Register an Expo push token")
def register(payload: RegisterIn, db: Session = Depends(get_db)) -> RegisterOut:
    register_token(db, wallet_id=payload.wallet_id, expo_push_token=payload.expo_push_token)
    return RegisterOut(wallet_id=payload.wallet_id, registered=True)


class TestPushIn(BaseModel):
    wallet_id: str
    title: str = "Vibe2Nite"
    body: str = "Hello from Vibe2Nite 🎶"


@router.post("/test", summary="Send a test push (admin/debug)")
def test_push(payload: TestPushIn, db: Session = Depends(get_db)):
    return send_push(db, wallet_id=payload.wallet_id, title=payload.title, body=payload.body)
