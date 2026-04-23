# -*- coding: utf-8 -*-
"""Feedback route."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.feedback import FeedbackIn, FeedbackOut
from app.services.feedback_service import apply_feedback

router = APIRouter(tags=["feedback"])


@router.post("/feedback", response_model=FeedbackOut, summary="Submit a vibe vote")
def submit_feedback(payload: FeedbackIn, db: Session = Depends(get_db)) -> FeedbackOut:
    """Record a user vote (**busy / dead / good**) and recompute the venue vibe score."""
    return apply_feedback(db, payload)
