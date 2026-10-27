from pydantic import BaseModel

from app.schemas.itinerary import DayPlan

class GeneratedPlan(BaseModel):
    days: list[DayPlan]

class ItineraryGenerationError(Exception):
    """The LLM couldn't produce a usable itinerary."""
