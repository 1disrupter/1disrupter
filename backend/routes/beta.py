"""
AlphaAI Beta Spots & Waitlist — Public endpoints.
"""
import os
import re
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from database import db

logger = logging.getLogger("AlphaAI.Beta")

router = APIRouter(prefix="/api/public", tags=["Public"])

BETA_SPOTS_TOTAL = int(os.environ.get("BETA_SPOTS_TOTAL", 50))

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class WaitlistEntry(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    note: Optional[str] = Field(None, max_length=500)


@router.get("/beta-spots")
async def get_beta_spots():
    used = await db.users.count_documents({"is_beta_tester": True})
    remaining = max(BETA_SPOTS_TOTAL - used, 0)
    return {"total": BETA_SPOTS_TOTAL, "used": used, "remaining": remaining}


@router.post("/waitlist")
async def join_waitlist(entry: WaitlistEntry, request: Request):
    # Validate email format
    if not EMAIL_RE.match(entry.email):
        raise HTTPException(status_code=422, detail="Invalid email format")

    email_lower = entry.email.strip().lower()

    # Rate limit: max 3 submissions per IP per hour
    client_ip = request.client.host if request.client else "unknown"
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    ip_count = await db.waitlist.count_documents({
        "ip": client_ip,
        "created_at": {"$gte": one_hour_ago}
    })
    if ip_count >= 3:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

    # Idempotent: if email already exists, return success silently
    existing = await db.waitlist.find_one({"email": email_lower}, {"_id": 0, "id": 1})
    if existing:
        return {"success": True}

    doc = {
        "id": str(uuid.uuid4()),
        "email": email_lower,
        "note": (entry.note or "").strip() or None,
        "ip": client_ip,
        "created_at": datetime.now(timezone.utc),
    }
    await db.waitlist.insert_one(doc)
    logger.info(f"Waitlist signup: {email_lower}")
    return {"success": True}
