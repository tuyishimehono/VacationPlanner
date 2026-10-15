from fastapi import FastAPI
from app.routers import trips


app = FastAPI(title="Vacation Planner")

app.include_router(trips.router)

@app.get("/")
def root():
    return {"message": "Vacation Planner API"}
    