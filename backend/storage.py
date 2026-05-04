from datetime import datetime

checkins = []

def add_checkin(entry):
    checkins.append(entry)

def get_recent_checkins(venue_id, minutes=15):
    now = datetime.utcnow()
    return [
        c for c in checkins
        if c["venueId"] == venue_id and
        (now - c["timestamp"]).total_seconds() < minutes * 60
    ]
