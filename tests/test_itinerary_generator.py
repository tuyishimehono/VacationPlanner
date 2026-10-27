import pytest

from app.schemas.itinerary import DayPlan
from app.schemas.trip import Trip
from app.services import itinerary_generator
from app.services.providers.base import GeneratedPlan, ItineraryGenerationError

TRIP = Trip(id=1, owner_id=1, destination="Kigali", days=2, budget=500, trip_style="relaxed")

def fake_provider(name, calls):
    def generate_plan(system, user):
        calls.append(name)
        return GeneratedPlan(days=[DayPlan(day=i, activities=["Walk"]) for i in range(1, TRIP.days + 1)])
    return generate_plan

@pytest.fixture
def calls(monkeypatch):
    calls = []
    monkeypatch.setitem(itinerary_generator.PROVIDERS, "claude", fake_provider("claude", calls))
    monkeypatch.setitem(itinerary_generator.PROVIDERS, "gemini", fake_provider("gemini", calls))
    return calls

@pytest.mark.parametrize("provider", ["claude", "gemini"])
def test_uses_provider_from_env(monkeypatch, calls, provider):
    monkeypatch.setenv("LLM_PROVIDER", provider)
    days = itinerary_generator.generate_itinerary(TRIP)
    assert calls == [provider]
    assert [d.day for d in days] == [1, 2]

def test_defaults_to_claude(monkeypatch, calls):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    itinerary_generator.generate_itinerary(TRIP)
    assert calls == ["claude"]

def test_unknown_provider(monkeypatch, calls):
    monkeypatch.setenv("LLM_PROVIDER", "gpt")
    with pytest.raises(ItineraryGenerationError, match="Unknown LLM_PROVIDER"):
        itinerary_generator.generate_itinerary(TRIP)
    assert calls == []
