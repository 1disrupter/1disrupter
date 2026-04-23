# -*- coding: utf-8 -*-
"""Seed sample venues + vibe data. Idempotent — skips if rows already exist."""
from datetime import datetime, timezone

from app.core.database import SessionLocal, engine, Base
from app.models import Venue, Vibe
from app.models.venue import VenueCategory
from app.services.scoring import compute_vibe_score, crowd_level_from_score

SEED = [
    # name, category, lat, lng, manual, social, votes, time, boost
    ("La Terraza Rooftop",      VenueCategory.club,        40.7308, -73.9973, 9.2, 8.8, 8.5, 9.0, 7.5),
    ("El Pimpi Bar",            VenueCategory.live_music,  40.7420, -73.9890, 8.5, 8.2, 8.0, 7.8, 6.5),
    ("Local Tapas Spot",        VenueCategory.bar,         40.7250, -74.0020, 7.0, 6.5, 7.2, 6.8, 5.0),
    ("Neon Halo",               VenueCategory.club,        40.7280, -73.9910, 8.8, 8.4, 8.2, 8.6, 7.0),
    ("Velvet Underground Lounge", VenueCategory.bar,       40.7190, -73.9600, 6.0, 5.5, 6.2, 5.8, 4.0),
    ("Basement 77",             VenueCategory.club,        40.7050, -74.0090, 4.2, 3.8, 4.0, 4.5, 3.0),
    ("The Sunken Stage",        VenueCategory.live_music,  40.7515, -73.9760, 7.8, 7.2, 7.5, 7.0, 5.5),
    ("Copper Canary",           VenueCategory.bar,         40.7390, -74.0050, 8.0, 7.5, 7.8, 7.2, 6.0),
    ("Room 9",                  VenueCategory.club,        40.7165, -73.9880, 3.5, 3.0, 3.2, 3.8, 2.5),
    ("Jupiter Jazz Den",        VenueCategory.live_music,  40.7200, -74.0015, 7.8, 7.0, 7.5, 7.0, 5.8),
    ("Last Call Alley",         VenueCategory.bar,         40.7085, -73.9570, 2.5, 2.0, 2.2, 2.8, 1.5),
    ("Static Sound Club",       VenueCategory.live_music,  40.7345, -73.9820, 8.9, 8.6, 8.3, 8.4, 7.0),
]


def run_seed() -> None:
    Base.metadata.create_all(bind=engine)  # no-op if migrations already applied
    db = SessionLocal()
    try:
        if db.query(Venue).count() > 0:
            print("[seed] venues already exist — skipping.")
            return
        now = datetime.now(timezone.utc)
        for name, cat, lat, lng, ms, sa, uv, tp, vb in SEED:
            venue = Venue(name=name, category=cat, latitude=lat, longitude=lng)
            db.add(venue)
            db.flush()
            signals = {
                "manual_score": ms, "social_activity": sa, "user_votes": uv,
                "time_prediction": tp, "venue_boost": vb,
            }
            score = compute_vibe_score(signals)
            db.add(Vibe(
                venue_id=venue.id,
                manual_score=ms, social_activity=sa, user_votes=uv,
                time_prediction=tp, venue_boost=vb,
                vibe_score=score,
                crowd_level=crowd_level_from_score(score),
                last_updated=now,
            ))
        db.commit()
        print(f"[seed] inserted {len(SEED)} venues.")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
