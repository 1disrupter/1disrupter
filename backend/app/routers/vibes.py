from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.vibe import TopVibesResponse
from app.services.recommendations import get_top_vibes

router = APIRouter(prefix="/vibes", tags=["vibes"])

@router.get("/top", response_model=TopVibesResponse)
def vibes_top(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(50.0),
    db: Session = Depends(get_db),
):
    results = get_top_vibes(db, lat=lat, lng=lng, radius_km=radius_km)

    return TopVibesResponse(
        best_overall=results.best_overall,
        live_music=results.live_music,
        hidden_gem=results.hidden_gem,
    )



    # Get Pydantic model
    results = get_top_vibes(db, lat=lat, lng=lng, radius_km=radius_km)

    # Convert to dict so .get() works
    results_dict = results.model_dump()

    # Fallback object matching schema
    fallback = {
        "venue": {
            "id": None,
            "name": "Coming soon",
            "address": "",
            "latitude": None,
            "longitude": None,
            "category": None,
            "is_verified": False,
        },
        "vibe": {
            "venue_id": None,
            "vibe_score": 0,
            "crowd_level": 0,
            "last_updated": None,
            "signals": {},
        },
        "distance_km": 0,
        "placeholder": True,
    }

    return {
        "best_overall": results_dict.get("best_overall") or fallback,
        "live_music": results_dict.get("live_music") or fallback,
        "hidden_gem": results_dict.get("hidden_gem") or fallback,
    }


