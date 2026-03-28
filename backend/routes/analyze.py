from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

try:
    from ..services.openai_client import OpenAIAnalysisClient
    from ..services.tinyfish_client import (
        TinyFishClient,
        TinyFishConfigError,
        get_default_community_urls,
        get_default_official_urls,
    )
except ImportError:
    from services.openai_client import OpenAIAnalysisClient
    from services.tinyfish_client import (
        TinyFishClient,
        TinyFishConfigError,
        get_default_community_urls,
        get_default_official_urls,
    )


router = APIRouter(prefix="/analyze", tags=["analysis"])


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    age: int = Field(..., ge=0, le=120)
    nationality: str
    years_in_singapore: float = Field(..., ge=0)
    pass_type: str
    profession: str
    monthly_salary: float = Field(..., ge=0)
    education: str
    marital_status: str
    spouse_status: str | None = None
    children_count: int = Field(..., ge=0)
    family_ties_in_singapore: bool
    prior_rejections: int = Field(..., ge=0)
    language_ability: str
    notes: str | None = None
    official_urls: list[str] = Field(
        default_factory=list,
        description="Optional official source URLs to prioritize during retrieval.",
    )
    community_urls: list[str] = Field(
        default_factory=list,
        description="Optional forum or community URLs to prioritize during retrieval.",
    )
    extra_notes: str | None = Field(
        default=None,
        description="Optional free-form notes from the user.",
    )


class AnalyzeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    readiness_score: int
    eligibility_signal: str
    official_takeaways: list[str]
    community_takeaways: list[str]
    top_strengths: list[str]
    top_risks: list[str]
    missing_documents: list[str]
    recommended_actions: list[str]
    confidence_notes: list[str]
    data_sources_used: dict[str, Any]
    error_note: str | None = None


FALLBACK_RESPONSE = {
    "readiness_score": 72,
    "eligibility_signal": "moderate",
    "official_takeaways": [
        "ICA PR assessment considers the full profile and supporting documents.",
        "A complete application package helps reduce avoidable review friction.",
    ],
    "community_takeaways": [
        "Applicants often discuss salary stability and time in Singapore as soft signals.",
        "Community cases are anecdotal and should not be treated as approval rules.",
    ],
    "top_strengths": [
        "Stable work history",
        "Relevant professional background",
    ],
    "top_risks": [
        "Limited family ties in Singapore",
    ],
    "missing_documents": [
        "Payslips",
        "Employer letter",
    ],
    "recommended_actions": [
        "Prepare supporting employment documents",
    ],
    "confidence_notes": [
        "Fallback response used due to unavailable external services",
    ],
    "data_sources_used": {
        "official_source": "ICA PR guidance",
        "community_source": "Reddit PR discussion thread",
    },
    "error_note": None,
}


def get_source_label(
    context: list[dict[str, Any]],
    fallback_label: str,
) -> str:
    if context and isinstance(context[0], dict):
        return context[0].get("title") or context[0].get("url") or fallback_label
    return fallback_label


def build_applicant_profile(request: AnalyzeRequest) -> dict[str, Any]:
    return {
        "age": request.age,
        "nationality": request.nationality,
        "years_in_singapore": request.years_in_singapore,
        "pass_type": request.pass_type,
        "profession": request.profession,
        "monthly_salary": request.monthly_salary,
        "education": request.education,
        "marital_status": request.marital_status,
        "spouse_status": request.spouse_status,
        "children_count": request.children_count,
        "family_ties_in_singapore": request.family_ties_in_singapore,
        "prior_rejections": request.prior_rejections,
        "language_ability": request.language_ability,
        "notes": request.notes,
        "extra_notes": request.extra_notes,
    }


def build_fallback_response(
    official_context: list[dict[str, Any]],
    community_context: list[dict[str, Any]],
    error_note: str,
) -> dict[str, Any]:
    response = dict(FALLBACK_RESPONSE)
    confidence_notes = list(FALLBACK_RESPONSE["confidence_notes"])
    if official_context or community_context:
        confidence_notes.append(
            "Some retrieval context was available, but the final analysis used the fallback response."
        )
    response["confidence_notes"] = confidence_notes
    response["data_sources_used"] = {
        "official_source": get_source_label(official_context, "ICA PR guidance"),
        "community_source": get_source_label(
            community_context,
            "Reddit PR discussion thread",
        ),
    }
    response["error_note"] = error_note
    return response


@router.post("", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> dict[str, Any]:
    official_context = []
    community_context = []
    retrieval_issue: str | None = None

    try:
        tinyfish_client = TinyFishClient()
    except TinyFishConfigError as exc:
        tinyfish_client = None
        retrieval_issue = str(exc)

    if tinyfish_client:
        try:
            official_context = tinyfish_client.collect_context(
                query="Singapore PR official guidance, requirements, and supporting documents",
                urls=request.official_urls or get_default_official_urls(),
                source_type="official",
            )
            community_context = tinyfish_client.collect_context(
                query="Singapore PR applicant experiences, approval patterns, and rejection concerns",
                urls=request.community_urls or get_default_community_urls(),
                source_type="community",
            )
        except Exception as exc:
            retrieval_issue = f"TinyFish retrieval failed: {exc}"
            official_context = []
            community_context = []

    try:
        analysis_client = OpenAIAnalysisClient()
        result = analysis_client.analyze_profile(
            applicant_profile=build_applicant_profile(request),
            official_context=official_context,
            community_context=community_context,
            extra_notes=request.extra_notes or request.notes,
        )
        if retrieval_issue:
            result["confidence_notes"] = list(result.get("confidence_notes", [])) + [
                retrieval_issue
            ]
        result.setdefault(
            "data_sources_used",
            {
                "official_source": "ICA PR guidance",
                "community_source": "Reddit PR discussion thread",
            },
        )
        result.setdefault("error_note", None)
        return result
    except Exception as exc:
        error_note = f"OpenAI analysis unavailable: {exc}"
        if retrieval_issue:
            error_note = f"{error_note}. {retrieval_issue}"
        return build_fallback_response(
            official_context=official_context,
            community_context=community_context,
            error_note=error_note,
        )
