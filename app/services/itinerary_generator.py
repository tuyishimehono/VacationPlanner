import os

from dotenv import load_dotenv

from app.prompts import SYSTEM_PROMPT, build_user_prompt
from app.schemas.itinerary import DayPlan
from app.schemas.trip import Trip
from app.services.providers import claude, gemini
from app.services.providers.base import ItineraryGenerationError

load_dotenv()

PROVIDERS = {
    "claude": claude.generate_plan,
    "gemini": gemini.generate_plan,
}

def generate_itinerary(trip: Trip) -> list[DayPlan]:
    provider = os.getenv("LLM_PROVIDER", "claude").lower()
    if provider not in PROVIDERS:
        raise ItineraryGenerationError(
            f"Unknown LLM_PROVIDER '{provider}', expected one of: {', '.join(PROVIDERS)}"
        )

    plan = PROVIDERS[provider](SYSTEM_PROMPT, build_user_prompt(trip))

    if [d.day for d in plan.days] != list(range(1, trip.days + 1)):
        raise ItineraryGenerationError(
            f"Expected days 1-{trip.days}, got {len(plan.days)} days"
        )
    return plan.days
