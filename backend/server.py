# -*- coding: utf-8 -*-
"""
Vibe2Nite - FastAPI backend
Real-time nightlife recommendations powered by a Vibe Score.
"""
import os
import uuid
import math
from datetime import datetime, timezone
from typing import Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv()

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

WEIGHTS = {
    "manual_score": 0.25,
    "social_activity": 0.25,
    "user_votes": 0.25,
    "time_prediction": 0.15,
    "venue_boost": 0.10,
}
VOTE_DELTAS = {"busy": 1.0, "good": 0.5, "dead": -1.0}

app = FastAPI(title="Vibe2Nite API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
venues_col = db.venues
vibes_col = db.vibes


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
CategoryT = Literal["bar", "club", "live_music"]
CrowdT = Literal["busy", "medium", "dead"]
VoteT = Literal["busy", "dead", "good"]


class Venue(BaseModel):
    id: str
    name: str
    category: CategoryT
    latitude: float
    longitude: float


class Signals(BaseModel):
    manual_score: float = 0.0
    social_activity: float = 0.0
    user_votes: float = 0.0
    time_prediction: float = 0.0
    venue_boost: float = 0.0


class VibeData(BaseModel):
    venue_id: str
    vibe_score: float
    crowd_level: CrowdT
    last_updated: str
    signals: Signals


class VibeResult(BaseModel):
    venue: Venue
    vibe: VibeData
    distance_km: Optional[float] = None


class TopVibesResponse(BaseModel):
    best_overall: Optional[VibeResult]
    live_music: Optional[VibeResult]
    hidden_gem: Optional[VibeResult]


class FeedbackIn(BaseModel):
    venue_id: str = Field(..., min_length=1)
    vote: VoteT


class FeedbackOut(BaseModel):
    venue_id: str
    new_vibe_score: float
    new_crowd_level: CrowdT
    updated_at: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def compute_vibe_score(signals: dict) -> float:
    """Weighted sum capped at 10."""
    score = sum(float(signals.get(k, 0.0)) * w for k, w in WEIGHTS.items())
    return round(min(max(score, 0.0), 10.0), 2)


def crowd_level_from_score(score: float) -> CrowdT:
    if score >= 8:
        return "busy"
    if score >= 5:
        return "medium"
    return "dead"


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return round(2 * R * math.asin(math.sqrt(a)), 3)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def build_result(venue_doc: dict, vibe_doc: dict,
                       user_lat: Optional[float], user_lng: Optional[float]) -> VibeResult:
    venue = Venue(
        id=venue_doc["id"],
        name=venue_doc["name"],
        category=venue_doc["category"],
        latitude=venue_doc["latitude"],
        longitude=venue_doc["longitude"],
    )
    vibe = VibeData(
        venue_id=vibe_doc["venue_id"],
        vibe_score=vibe_doc["vibe_score"],
        crowd_level=vibe_doc["crowd_level"],
        last_updated=vibe_doc["last_updated"],
        signals=Signals(**vibe_doc.get("signals", {})),
    )
    dist = None
    if user_lat is not None and user_lng is not None:
        dist = haversine_km(user_lat, user_lng, venue.latitude, venue.longitude)
    return VibeResult(venue=venue, vibe=vibe, distance_km=dist)


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------
SEED_VENUES = [
    # NYC-ish coordinates so devs can test with lat=40.73, lng=-73.99
    {"name": "Neon Halo",       "category": "club",        "latitude": 40.7308, "longitude": -73.9973,
     "signals": {"manual_score": 9.2, "social_activity": 8.8, "user_votes": 8.5, "time_prediction": 9.0, "venue_boost": 7.5}},
    {"name": "Velvet Underground Lounge", "category": "bar", "latitude": 40.7250, "longitude": -74.0020,
     "signals": {"manual_score": 7.0, "social_activity": 6.5, "user_votes": 7.2, "time_prediction": 6.8, "venue_boost": 5.0}},
    {"name": "The Brasswork",   "category": "live_music",  "latitude": 40.7420, "longitude": -73.9890,
     "signals": {"manual_score": 8.5, "social_activity": 8.2, "user_votes": 8.0, "time_prediction": 7.8, "venue_boost": 6.5}},
    {"name": "Midnight Mezcal", "category": "bar",         "latitude": 40.7190, "longitude": -73.9600,
     "signals": {"manual_score": 6.0, "social_activity": 5.5, "user_votes": 6.2, "time_prediction": 5.8, "venue_boost": 4.0}},
    {"name": "Basement 77",     "category": "club",        "latitude": 40.7050, "longitude": -74.0090,
     "signals": {"manual_score": 4.2, "social_activity": 3.8, "user_votes": 4.0, "time_prediction": 4.5, "venue_boost": 3.0}},
    {"name": "The Sunken Stage","category": "live_music",  "latitude": 40.7515, "longitude": -73.9760,
     "signals": {"manual_score": 5.5, "social_activity": 6.0, "user_votes": 5.8, "time_prediction": 5.5, "venue_boost": 4.5}},
    {"name": "Copper Canary",   "category": "bar",         "latitude": 40.7390, "longitude": -74.0050,
     "signals": {"manual_score": 8.0, "social_activity": 7.5, "user_votes": 7.8, "time_prediction": 7.2, "venue_boost": 6.0}},
    {"name": "Room 9",          "category": "club",        "latitude": 40.7165, "longitude": -73.9880,
     "signals": {"manual_score": 3.5, "social_activity": 3.0, "user_votes": 3.2, "time_prediction": 3.8, "venue_boost": 2.5}},
    {"name": "Jupiter Jazz Den","category": "live_music",  "latitude": 40.7280, "longitude": -74.0015,
     "signals": {"manual_score": 7.8, "social_activity": 7.0, "user_votes": 7.5, "time_prediction": 7.0, "venue_boost": 5.8}},
    {"name": "Last Call Alley", "category": "bar",         "latitude": 40.7085, "longitude": -73.9570,
     "signals": {"manual_score": 2.5, "social_activity": 2.0, "user_votes": 2.2, "time_prediction": 2.8, "venue_boost": 1.5}},
]


async def seed_if_empty() -> None:
    count = await venues_col.count_documents({})
    if count > 0:
        return
    for v in SEED_VENUES:
        venue_id = str(uuid.uuid4())
        await venues_col.insert_one({
            "id": venue_id,
            "name": v["name"],
            "category": v["category"],
            "latitude": v["latitude"],
            "longitude": v["longitude"],
        })
        signals = v["signals"]
        score = compute_vibe_score(signals)
        await vibes_col.insert_one({
            "venue_id": venue_id,
            "vibe_score": score,
            "crowd_level": crowd_level_from_score(score),
            "last_updated": now_iso(),
            "signals": signals,
        })


@app.on_event("startup")
async def startup() -> None:
    await venues_col.create_index("id", unique=True)
    await vibes_col.create_index("venue_id", unique=True)
    await seed_if_empty()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "vibe2nite", "time": now_iso()}


@app.get("/api/vibes/top", response_model=TopVibesResponse)
async def vibes_top(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(50.0, gt=0, le=500),
):
    """Return best_overall, live_music, and hidden_gem for the given location."""
    # Pull all venues + vibes; filter by radius
    venues = {v["id"]: v async for v in venues_col.find({}, {"_id": 0})}
    if not venues:
        return TopVibesResponse(best_overall=None, live_music=None, hidden_gem=None)

    pairs = []
    async for vibe in vibes_col.find({}, {"_id": 0}):
        venue = venues.get(vibe["venue_id"])
        if not venue:
            continue
        dist = haversine_km(lat, lng, venue["latitude"], venue["longitude"])
        if dist > radius_km:
            continue
        pairs.append((venue, vibe, dist))

    if not pairs:
        return TopVibesResponse(best_overall=None, live_music=None, hidden_gem=None)

    # Best overall = highest score
    best_pair = max(pairs, key=lambda p: p[1]["vibe_score"])
    # Hidden gem = lowest score
    gem_pair = min(pairs, key=lambda p: p[1]["vibe_score"])
    # Best live_music, fallback to best_overall
    lm_candidates = [p for p in pairs if p[0]["category"] == "live_music"]
    lm_pair = max(lm_candidates, key=lambda p: p[1]["vibe_score"]) if lm_candidates else best_pair

    return TopVibesResponse(
        best_overall=await build_result(*best_pair[:2], lat, lng),
        live_music=await build_result(*lm_pair[:2], lat, lng),
        hidden_gem=await build_result(*gem_pair[:2], lat, lng),
    )


@app.post("/api/feedback", response_model=FeedbackOut)
async def submit_feedback(payload: FeedbackIn):
    """Record a user vote and recompute the venue's vibe score."""
    venue = await venues_col.find_one({"id": payload.venue_id}, {"_id": 0})
    if not venue:
        raise HTTPException(status_code=404, detail="venue_id not found")

    vibe = await vibes_col.find_one({"venue_id": payload.venue_id}, {"_id": 0})
    if not vibe:
        # initialise if somehow missing
        vibe = {
            "venue_id": payload.venue_id,
            "vibe_score": 0.0,
            "crowd_level": "dead",
            "last_updated": now_iso(),
            "signals": Signals().model_dump(),
        }

    signals = dict(vibe.get("signals", {}))
    delta = VOTE_DELTAS[payload.vote]
    signals["user_votes"] = max(0.0, min(10.0, float(signals.get("user_votes", 0.0)) + delta))

    new_score = compute_vibe_score(signals)
    new_crowd = crowd_level_from_score(new_score)
    updated_at = now_iso()

    await vibes_col.update_one(
        {"venue_id": payload.venue_id},
        {"$set": {
            "signals": signals,
            "vibe_score": new_score,
            "crowd_level": new_crowd,
            "last_updated": updated_at,
        }},
        upsert=True,
    )

    return FeedbackOut(
        venue_id=payload.venue_id,
        new_vibe_score=new_score,
        new_crowd_level=new_crowd,
        updated_at=updated_at,
    )


@app.get("/api/venues")
async def list_venues():
    """Convenience endpoint — list all seeded venues with their current vibes."""
    venues = {v["id"]: v async for v in venues_col.find({}, {"_id": 0})}
    results = []
    async for vibe in vibes_col.find({}, {"_id": 0}):
        venue = venues.get(vibe["venue_id"])
        if venue:
            results.append({"venue": venue, "vibe": vibe})
    return {"count": len(results), "items": results}
