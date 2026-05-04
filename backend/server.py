# -*- coding: utf-8 -*-
"""Entrypoint shim for supervisor (uvicorn server:app)."""
from app.main import app  # noqa: F401
if __name__ == "__main__":
    import seed_benalmadena
    
from fastapi import FastAPI
from datetime import datetime
from models import CheckIn
from storage import add_checkin, get_recent_checkins
from logic import calculate_reward

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Vibe2nite API running"}

@app.post("/api/checkin")
def checkin(data: CheckIn):
    entry = {
        "venueId": data.venueId,
        "deviceId": data.deviceId,
        "timestamp": datetime.utcnow()
    }

    add_checkin(entry)

    group = get_recent_checkins(data.venueId)

    unique_devices = list(set([c["deviceId"] for c in group]))
    group_size = len(unique_devices)

    reward = calculate_reward(group_size)

    return {
        "success": True,
        "group_size": group_size,
        "reward": reward
    }
