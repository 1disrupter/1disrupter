# -*- coding: utf-8 -*-
"""Schemas for venues + vibe data responses."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.venue import VenueCategory
from app.models.vibe import CrowdLevel


class VenueOut(BaseModel):
    id: str
    name: str
    category: VenueCategory
    latitude: float
    longitude: float
    is_verified: bool = False

    model_config = {"from_attributes": True}


class SignalsOut(BaseModel):
    manual_score: float
    social_activity: float
    user_votes: float
    time_prediction: float
    venue_boost: float


class VibeOut(BaseModel):
    venue_id: str
    vibe_score: float = Field(..., ge=0, le=10)
    crowd_level: CrowdLevel
    last_updated: datetime
    signals: SignalsOut


class VibeResult(BaseModel):
    venue: VenueOut
    vibe: VibeOut
    distance_km: Optional[float] = None


class TopVibesResponse(BaseModel):
    best_overall: Optional[VibeResult]
    live_music: Optional[VibeResult]
    hidden_gem: Optional[VibeResult]
