from pydantic import BaseModel

class CheckIn(BaseModel):
    venueId: str
    deviceId: str
