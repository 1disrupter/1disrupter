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



