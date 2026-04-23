# -*- coding: utf-8 -*-
"""Feedback endpoint schemas."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.feedback import VoteType
from app.models.vibe import CrowdLevel


class FeedbackIn(BaseModel):
    venue_id: str = Field(..., min_length=1, description="Target venue UUID")
    vote: VoteType = Field(..., description="busy | dead | good")


class FeedbackOut(BaseModel):
    venue_id: str
    new_vibe_score: float
    new_crowd_level: CrowdLevel
    updated_at: datetime
