from fastapi.testclient import TestClient
from app.main import app
from app.schemas.itinerary import DayPlan

client = TestClient(app)

def auth_headers(email="traveler@example.com", password="secret123"):
    client.post("/auth/register", json={"email": email, "password": password})
    r = client.post("/auth/login", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}

def test_create_and_get_trip():
    headers = auth_headers()
    r = client.post("/trips/", headers=headers, json= {"destination": "Lisbon", "days":"15", "budget": "300000", "trip_style":"budget" })
    assert r.status_code == 201
    trip_id = r.json()["id"]
    assert client.get(f"/trips/{trip_id}", headers=headers).json()["destination"] == "Lisbon"

def test_trips_require_auth():
    assert client.get("/trips/").status_code == 401

def test_other_users_trip_is_hidden():
    owner = auth_headers("owner@example.com")
    other = auth_headers("other@example.com")
    trip_id = client.post("/trips/", headers=owner, json={"destination": "Rome", "days": 3, "budget": 1000, "trip_style": "luxury"}).json()["id"]
    assert client.get(f"/trips/{trip_id}", headers=other).status_code == 404

def test_create_and_get_itinerary(monkeypatch):
    days = [DayPlan(day=1, activities=["Eiffel Tower", "Seine River Walk"])]
    monkeypatch.setattr("app.routers.itinerary.generate_itinerary", lambda trip: days)
    headers = auth_headers()
    trip_id = client.post("/trips/", headers=headers, json={"destination": "Paris", "days": 1, "budget": 2000, "trip_style": "culture"}).json()["id"]
    itinerary = {"trip_id": trip_id, "days": [d.model_dump() for d in days]}
    assert client.post("/itineraries/", headers=headers, json={"trip_id": trip_id}).status_code == 201
    assert client.get(f"/itineraries/{trip_id}", headers=headers).json() == itinerary
    assert client.post("/itineraries/", headers=headers, json={"trip_id": trip_id}).status_code == 409
