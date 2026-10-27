from functools import cache

import httpx
import httpx2
from google import genai
from google.genai import errors, types

from app.services.providers.base import GeneratedPlan, ItineraryGenerationError

MODEL = "gemini-3.8-flash"

CONNECTION_ERRORS = (httpx.TransportError, httpx2.TransportError)

BLOCKED_REASONS = {
    types.FinishReason.SAFETY,
    types.FinishReason.PROHIBITED_CONTENT,
    types.FinishReason.BLOCKLIST,
    types.FinishReason.SPII,
    types.FinishReason.RECITATION,
}

@cache
def _client() -> genai.Client:
    return genai.Client()

def generate_plan(system: str, user: str) -> GeneratedPlan:
    try:
        response = _client().models.generate_content(
            model=MODEL,
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system,
                response_mime_type="application/json",
                response_schema=GeneratedPlan,
                max_output_tokens=16000,
            ),
        )
    except ValueError as e:
        raise ItineraryGenerationError("Gemini API key is missing") from e
    except errors.ClientError as e:
        if e.code == 429:
            raise ItineraryGenerationError("AI service is busy, try again shortly") from e
        raise ItineraryGenerationError(f"AI service error ({e.code})") from e
    except errors.ServerError as e:
        raise ItineraryGenerationError(f"AI service error ({e.code})") from e
    except CONNECTION_ERRORS as e:
        raise ItineraryGenerationError("Could not reach the AI service") from e

    if not response.candidates:
        raise ItineraryGenerationError("The AI declined to plan this trip")
    finish_reason = response.candidates[0].finish_reason
    if finish_reason in BLOCKED_REASONS:
        raise ItineraryGenerationError("The AI declined to plan this trip")
    if finish_reason == types.FinishReason.MAX_TOKENS:
        raise ItineraryGenerationError("The itinerary was too long and got cut off")

    if not isinstance(response.parsed, GeneratedPlan):
        raise ItineraryGenerationError("The AI returned an itinerary in the wrong format")
    return response.parsed
