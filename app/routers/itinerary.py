from fastapi import APIRouter, HTTPException

from app import db
from app.dependencies import CurrentUser, get_owned_trip
from app.schemas.itinerary import Itinerary

router = APIRouter(prefix="/itineraries", tags=["itineraries"])

@router.post("/", response_model=Itinerary, status_code=201)
def create_itinerary(data: Itinerary, user: CurrentUser):
    get_owned_trip(data.trip_id, user)
    if data.trip_id in db.itineraries:
        raise HTTPException(status_code=409, detail="Itinerary already exists for this trip")
    db.itineraries[data.trip_id] = data
    return data

@router.get("/{trip_id}", response_model=Itinerary)
def get_itinerary(trip_id: int, user: CurrentUser):
    get_owned_trip(trip_id, user)
    if trip_id not in db.itineraries:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    return db.itineraries[trip_id]
