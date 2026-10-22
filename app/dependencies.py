from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app import db
from app.schemas.trip import Trip
from app.schemas.user import UserInDB
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
    user_id = decode_access_token(token)
    if user_id is None or user_id not in db.users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db.users[user_id]

CurrentUser = Annotated[UserInDB, Depends(get_current_user)]

def get_owned_trip(trip_id: int, user: UserInDB) -> Trip:
    trip = db.trips.get(trip_id)
    if trip is None or trip.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip
