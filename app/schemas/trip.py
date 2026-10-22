from pydantic import BaseModel

class TripCreate(BaseModel):
    destination: str
    days : int
    budget: int
    trip_style: str

class Trip(TripCreate):
    id: int
    owner_id: int

class MessageResponse(BaseModel):
    message: str
