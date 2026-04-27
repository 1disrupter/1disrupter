import asyncio
from pymongo import MongoClient
from app.websocket.manager import manager
from app.services.vibe_scoring import calculate_vibe_score

client = MongoClient()
db = client.get_default_database()
venues = db["venues"]

async def run_vibe_updater():
    while True:
        all_venues = list(venues.find({}))
        for v in all_venues:
            signals = v.get("signals", {})
            score = calculate_vibe_score(signals)
            venues.update_one({"_id": v["_id"]}, {"$set": {"vibe_score": score}})

        # Push update to all connected clients
        await manager.broadcast({"type": "vibe_update"})

        # Wait 5 minutes
        await asyncio.sleep(300)
