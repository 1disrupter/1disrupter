# -*- coding: utf-8 -*-
"""Feedback service — records vote, updates user_votes signal, recomputes score."""
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Venue, Vibe, FeedbackLog
from app.models.feedback import VoteType
from app.schemas.feedback import FeedbackIn, FeedbackOut
from app.services.scoring import VOTE_DELTAS, compute_vibe_score, crowd_level_from_score


def apply_feedback(db: Session, payload: FeedbackIn) -> FeedbackOut:
    venue = db.get(Venue, payload.venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="venue_id not found"
        )

    vibe = db.get(Vibe, payload.venue_id)
    if not vibe:
        vibe = Vibe(venue_id=payload.venue_id)
        db.add(vibe)

    delta = VOTE_DELTAS[payload.vote.value]
    vibe.user_votes = max(0.0, min(10.0, float(vibe.user_votes or 0.0) + delta))

    new_score = compute_vibe_score(vibe.signals_dict())
    new_crowd = crowd_level_from_score(new_score)

    vibe.vibe_score = new_score
    vibe.crowd_level = new_crowd
    vibe.last_updated = datetime.now(timezone.utc)

    db.add(FeedbackLog(venue_id=payload.venue_id, vote=VoteType(payload.vote.value)))
    db.commit()
    db.refresh(vibe)

    return FeedbackOut(
        venue_id=vibe.venue_id,
        new_vibe_score=vibe.vibe_score,
        new_crowd_level=vibe.crowd_level,
        updated_at=vibe.last_updated,
    )
