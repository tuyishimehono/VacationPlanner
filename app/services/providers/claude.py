from functools import cache

import anthropic

from app.services.providers.base import GeneratedPlan, ItineraryGenerationError

MODEL = "claude-opus-5-5"

@cache
def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic()

def generate_plan(system: str, user: str) -> GeneratedPlan:
    try:
        response = _client().messages.parse(
            model=MODEL,
            max_tokens=16000,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_format=GeneratedPlan,
        )
    except TypeError as e:  # raised by the SDK when no API key is configured at all
        if "authentication" not in str(e):
            raise
        raise ItineraryGenerationError("Claude API key is missing") from e
    except anthropic.AuthenticationError as e:
        raise ItineraryGenerationError("Claude API key is missing or invalid") from e
    except anthropic.RateLimitError as e:
        raise ItineraryGenerationError("AI service is busy, try again shortly") from e
    except anthropic.APIConnectionError as e:
        raise ItineraryGenerationError("Could not reach the AI service") from e
    except anthropic.APIStatusError as e:
        raise ItineraryGenerationError(f"AI service error ({e.status_code})") from e

    if response.stop_reason == "refusal":
        raise ItineraryGenerationError("The AI declined to plan this trip")
    if response.stop_reason == "max_tokens":
        raise ItineraryGenerationError("The itinerary was too long and got cut off")

    return response.parsed_output
