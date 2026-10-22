from pydantic import BaseModel

class DayPlan(BaseModel):
    day: int
    activities: list[str]

class ItineraryCreate(BaseModel):
    trip_id: int
    days: list[DayPlan]

class Itinerary(BaseModel):
    trip_id: int
    days: list [DayPlan]

