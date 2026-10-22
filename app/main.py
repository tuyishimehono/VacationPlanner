from fastapi import FastAPI
from app.routers import auth, users, trips, itinerary


app = FastAPI(title="Vacation Planner")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(trips.router)
app.include_router(itinerary.router)

@app.get("/")
def root():
    return {"message": "Vacation Planner API"}
