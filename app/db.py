from itertools import count

from app.schemas.itinerary import Itinerary
from app.schemas.trip import Trip
from app.schemas.user import UserInDB

users: dict[int, UserInDB] = {}
trips: dict[int, Trip] = {}
itineraries: dict[int, Itinerary] = {} 

user_ids = count(1)
trip_ids = count(1)
