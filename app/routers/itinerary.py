from fastapi import APIRouter, HTTPException

from app import db
from app.dependencies import CurrentUser, get_owned_trip
from app.schemas.itinerary import Itinerary, ItineraryRequest
from app.services.itinerary_generator import ItineraryGenerationError, generate_itinerary

router = APIRouter(prefix="/itineraries", tags=["itineraries"])

@router.post(
        "/", 
        response_model=Itinerary, 
        status_code=201,
        summary="Generate an itinerary with AI",
        description="Reads the trip's destination, days, budget and style, asks an LLM to plan it, saves and returns the itinerary.",
        responses={404: {"description":"Trip not found"},
                   409: {"description": "Trip already has an itinerary"},
                   502: {"description": "The AI could not generate an itinerary"}},
        )
def create_itinerary(data: ItineraryRequest, user: CurrentUser):
    trip = get_owned_trip(data.trip_id, user)
    if trip.id in db.itineraries:
        raise HTTPException(status_code=409, detail="Itinerary already exists for this trip")
    try:
        days = generate_itinerary(trip)
    except ItineraryGenerationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    itinerary = Itinerary(trip_id=trip.id, days=days)
    db.itineraries[trip.id] = itinerary
    return itinerary

@router.get("/{trip_id}", response_model=Itinerary)
def get_itinerary(trip_id: int, user: CurrentUser):
    get_owned_trip(trip_id, user)
    if trip_id not in db.itineraries:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    return db.itineraries[trip_id]
