# -*- coding: utf-8 -*-
"""Feedback service — records vote, updates user_votes signal, recomputes score.

After the legacy score is written, we also fire the Signal-Engine refresh for
this venue so the response's `new_vibe_score` matches what the scheduler
would publish — no "disappearing vote" UX.
"""
import asyncio
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

    # Legacy bookkeeping (keeps compute_vibe_score + vibes.user_votes intact).
    delta = VOTE_DELTAS[payload.vote.value]
    vibe.user_votes = max(0.0, min(10.0, float(vibe.user_votes or 0.0) + delta))

    legacy_score = compute_vibe_score(vibe.signals_dict())
    vibe.vibe_score = legacy_score
    vibe.crowd_level = crowd_level_from_score(legacy_score)
    vibe.last_updated = datetime.now(timezone.utc)

    db.add(FeedbackLog(venue_id=payload.venue_id, vote=VoteType(payload.vote.value)))
    db.commit()

    # Fire the signal-engine refresh for this venue so the response's
    # new_vibe_score is the same number the scheduler will publish.
    new_score = legacy_score
    try:
        from app.services.scheduler import refresh_venue_signals  # local import avoids cycle
        result = asyncio.run(refresh_venue_signals(payload.venue_id))
        if isinstance(result, dict) and "vibe_score" in result:
            new_score = float(result["vibe_score"])
    except RuntimeError:
        # Called from within a running event loop (e.g. async tests). The
        # scheduler will catch up on its next tick — legacy score returned.
        pass
    except Exception:
        pass

    return FeedbackOut(
        venue_id=payload.venue_id,
        new_vibe_score=new_score,
        new_crowd_level=crowd_level_from_score(new_score),
        updated_at=datetime.now(timezone.utc),
    )
