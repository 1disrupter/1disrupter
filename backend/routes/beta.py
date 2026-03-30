"""
AlphaAI Beta Spots — Public endpoint for real-time beta availability.
"""
import os
from fastapi import APIRouter
from database import db

router = APIRouter(prefix="/api/public", tags=["Public"])

BETA_SPOTS_TOTAL = int(os.environ.get("BETA_SPOTS_TOTAL", 50))


@router.get("/beta-spots")
async def get_beta_spots():
    used = await db.users.count_documents({"is_beta_tester": True})
    remaining = max(BETA_SPOTS_TOTAL - used, 0)
    return {"total": BETA_SPOTS_TOTAL, "used": used, "remaining": remaining}
