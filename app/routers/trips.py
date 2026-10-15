from fastapi import APIRouter, HTTPException
from app.schemas.trip import Trip, TripCreate

router = APIRouter(prefix="/trips", tags=["trips"])
_trips: dict[int, Trip] = {}
_next_id = 1

@router.post("/", response_model = Trip, status_code=201)
def create_trip(data: TripCreate):
    global _next_id
    trip = Trip(id= _next_id, **data.model_dump())
    _trips[trip.id] = trip
    _next_id +=1
    return trip

@router.get("/", response_model=list[Trip])
def list_trips():
    return list(_trips.values())

@router.get("/{trip_id}", response_model=Trip)
def get_trip(trip_id: int):
    if trip_id not in _trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    return _trips[trip_id]

@router.put("/{trip_id}", response_model=Trip)
def update_trip(trip_id: int, updated_trip: TripCreate):
    if trip_id not in _trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    trip = Trip(id=trip_id, **updated_trip.model_dump())
    _trips[trip_id] = trip
    return trip


@router.delete("/trips/{trip_id}", response_model=Trip)
def delete_trip(trip_id: int):
    if(trip_id not in _trips):
        raise HTTPException(status_code=404, detail="Trip not found")

    del _trips[trip_id]
    return {"message": f"Trip {trip_id} deleted successfully"}