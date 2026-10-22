from fastapi import APIRouter

from app import db
from app.dependencies import CurrentUser, get_owned_trip
from app.schemas.trip import Trip, TripCreate, MessageResponse

router = APIRouter(prefix="/trips", tags=["trips"])

@router.post("/", response_model = Trip, status_code=201)
def create_trip(data: TripCreate, user: CurrentUser):
    trip = Trip(id=next(db.trip_ids), owner_id=user.id, **data.model_dump())
    db.trips[trip.id] = trip
    return trip

@router.get("/", response_model=list[Trip])
def list_trips(user: CurrentUser):
    return [t for t in db.trips.values() if t.owner_id == user.id]

@router.get("/{trip_id}", response_model=Trip)
def get_trip(trip_id: int, user: CurrentUser):
    return get_owned_trip(trip_id, user)

@router.put("/{trip_id}", response_model=Trip)
def update_trip(trip_id: int, updated_trip: TripCreate, user: CurrentUser):
    get_owned_trip(trip_id, user)
    trip = Trip(id=trip_id, owner_id=user.id, **updated_trip.model_dump())
    db.trips[trip_id] = trip
    return trip


@router.delete("/{trip_id}", response_model=MessageResponse)
def delete_trip(trip_id: int, user: CurrentUser):
    get_owned_trip(trip_id, user)
    del db.trips[trip_id]
    db.itineraries.pop(trip_id, None)
    return {"message": f"Trip {trip_id} deleted successfully"}
