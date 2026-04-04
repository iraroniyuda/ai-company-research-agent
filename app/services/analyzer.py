from google import genai
from google.genai import types
from pydantic import BaseModel, ConfigDict, ValidationError

from app.core.config import settings


class CompanyAnalysis(BaseModel):
    industry: str | None
    business_model: str | None
    summary: str | None
    use_case: str | None

    model_config = ConfigDict(extra="forbid")


def _fallback_analysis() -> CompanyAnalysis:
    return CompanyAnalysis(
        industry=None,
        business_model=None,
        summary=None,
        use_case=None,
    )


def analyze_company_description(description: str | None) -> CompanyAnalysis:
    if description is None or not description.strip():
        return _fallback_analysis()

    if not settings.gemini_api_key:
        return _fallback_analysis()

    client = genai.Client(api_key=settings.gemini_api_key)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                "Analyze the company description below and return JSON with exactly "
                "these keys only: industry, business_model, summary, use_case. "
                "Each value must be a string or null.\n\n"
                f"Company description:\n{description}"
            ),
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
            ),
        )

        if not response.text:
            return _fallback_analysis()

        return CompanyAnalysis.model_validate_json(response.text)
    except ValidationError as e:
        print(f"ANALYZER_VALIDATION_ERROR: {type(e).__name__}: {e}")
        return _fallback_analysis()
    except Exception as e:
        print(f"ANALYZER_ERROR: {type(e).__name__}: {e}")
        return _fallback_analysis()