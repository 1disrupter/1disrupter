# -*- coding: utf-8 -*-
"""Location pings — anonymous lat/lng/timestamp samples from mobile clients.

Stored in `user_location_pings`. The endpoint accepts an *optional* opaque
device_id (e.g. a random UUID generated once on-device) so we can detect
dwell/visit patterns server-side without any PII.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models import UserLocationPing


def record_ping(
    db: Session, *, lat: float, lng: float, timestamp: datetime,
    device_id: Optional[str] = None,
) -> UserLocationPing:
    row = UserLocationPing(lat=lat, lng=lng, timestamp=timestamp, device_id=device_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
