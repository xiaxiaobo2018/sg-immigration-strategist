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
    scoring_breakdown: dict[str, Any]
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
    "scoring_breakdown": {
        "rubric_name": "singapore_pr_readiness_v1",
        "preliminary_score": 72,
        "final_score": 72,
        "score_adjustment": {
            "direction": "none",
            "delta": 0,
            "driver": "none",
            "reason": "Fallback mode kept the final score aligned with the rubric baseline.",
        },
        "source_quality": {
            "official": {
                "level": "mixed",
                "label": "Official Support",
                "reason": "Some official PR guidance was available, but coverage was limited.",
            },
            "community": {
                "level": "thin",
                "label": "Community Signals",
                "reason": "Community evidence was light and should be treated cautiously.",
            },
        },
        "band_guidance": {
            "low": "0-49: early, weak, or highly incomplete PR profile",
            "moderate": "50-74: plausible PR profile with meaningful gaps or uncertainty",
            "strong": "75-100: well-developed PR profile with multiple positive signals",
        },
        "dimensions": [
            {
                "name": "residency_stability",
                "label": "Residency Stability",
                "score": 21,
                "max_score": 25,
                "reason": "Solid residency duration for a PR profile.",
            },
            {
                "name": "employment_foundation",
                "label": "Employment Foundation",
                "score": 20,
                "max_score": 28,
                "reason": "Employment footing and salary profile are reasonably supportive.",
            },
            {
                "name": "settlement_signals",
                "label": "Settlement Signals",
                "score": 4,
                "max_score": 15,
                "reason": "Limited explicit family anchoring signals were provided.",
            },
            {
                "name": "human_capital",
                "label": "Human Capital",
                "score": 8,
                "max_score": 10,
                "reason": "Education and language details support the profile.",
            },
            {
                "name": "documentation_readiness",
                "label": "Documentation Readiness",
                "score": 7,
                "max_score": 10,
                "reason": "Profile notes provide some evidence of application preparation.",
            },
            {
                "name": "reapplication_risk",
                "label": "Reapplication Risk",
                "score": 12,
                "max_score": 12,
                "reason": "No prior rejection history was provided.",
            },
        ],
    },
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


def score_years_in_singapore(years_in_singapore: float) -> tuple[int, str]:
    if years_in_singapore >= 8:
        return 25, "Long residency history in Singapore."
    if years_in_singapore >= 5:
        return 21, "Solid residency duration for a PR profile."
    if years_in_singapore >= 3:
        return 16, "Moderate residency duration with some track record."
    if years_in_singapore >= 1:
        return 10, "Limited residency duration; profile may still look early."
    return 4, "Very limited residency history in Singapore."


def score_employment_foundation(
    pass_type: str,
    monthly_salary: float,
    profession: str,
) -> tuple[int, str]:
    pass_type_normalized = pass_type.strip().lower()
    profession_present = bool(profession.strip())

    score = 0
    reasons: list[str] = []

    if "employment pass" in pass_type_normalized:
        score += 12
        reasons.append("Employment Pass profile suggests skilled employment footing.")
    elif "s pass" in pass_type_normalized:
        score += 9
        reasons.append("S Pass profile shows formal employment footing.")
    elif "entrepass" in pass_type_normalized:
        score += 9
        reasons.append("EntrePass profile shows formal business footing.")
    elif "dependent" in pass_type_normalized or "student" in pass_type_normalized:
        score += 4
        reasons.append("Current pass type provides less direct employment stability.")
    else:
        score += 6
        reasons.append("Pass type shows some Singapore-based status but with less clarity.")

    if monthly_salary >= 12000:
        score += 13
        reasons.append("Higher salary suggests stronger earning stability.")
    elif monthly_salary >= 8000:
        score += 11
        reasons.append("Salary level suggests solid earning stability.")
    elif monthly_salary >= 5000:
        score += 8
        reasons.append("Salary level provides moderate employment support.")
    elif monthly_salary >= 3000:
        score += 5
        reasons.append("Salary level provides limited employment support.")
    else:
        score += 2
        reasons.append("Lower salary weakens the employment signal.")

    if profession_present:
        score += 3

    return min(score, 28), " ".join(reasons)


def score_settlement_signals(
    marital_status: str,
    spouse_status: str | None,
    children_count: int,
    family_ties_in_singapore: bool,
) -> tuple[int, str]:
    score = 4
    reasons: list[str] = []

    if family_ties_in_singapore:
        score += 6
        reasons.append("Family ties in Singapore strengthen local anchoring.")

    if children_count > 0:
        score += 4
        reasons.append("Children add household settlement context.")

    if marital_status.strip().lower() in {"married", "engaged"}:
        score += 3
        reasons.append("Family unit can strengthen settlement framing.")

    if spouse_status and spouse_status.strip():
        score += 2
        reasons.append("Spouse status provides more household context.")

    if not reasons:
        reasons.append("Limited explicit family anchoring signals were provided.")

    return min(score, 15), " ".join(reasons)


def score_human_capital(
    education: str,
    language_ability: str,
) -> tuple[int, str]:
    education_normalized = education.strip().lower()
    language_present = bool(language_ability.strip())

    score = 0
    reasons: list[str] = []

    if any(level in education_normalized for level in ("phd", "doctor", "master")):
        score += 8
        reasons.append("Advanced education strengthens the profile.")
    elif any(level in education_normalized for level in ("bachelor", "degree", "diploma")):
        score += 6
        reasons.append("Post-secondary education supports the profile.")
    elif education_normalized:
        score += 4
        reasons.append("Education details provide some human-capital support.")
    else:
        reasons.append("Education information is thin.")

    if language_present:
        score += 2
        reasons.append("Language ability is documented.")

    return min(score, 10), " ".join(reasons)


def score_documentation_readiness(
    notes: str | None,
    extra_notes: str | None,
    profession: str,
    education: str,
) -> tuple[int, str]:
    score = 4
    reasons: list[str] = []

    if profession.strip():
        score += 2
    if education.strip():
        score += 2
    if notes and notes.strip():
        score += 3
        reasons.append("The profile includes supporting context in notes.")
    if extra_notes and extra_notes.strip():
        score += 2
        reasons.append("Extra notes improve context completeness.")

    combined_notes = " ".join(filter(None, [notes, extra_notes])).lower()
    if any(token in combined_notes for token in ("payslip", "employer", "tax", "cpf", "certificate")):
        score += 2
        reasons.append("The notes hint at documentation awareness.")

    if not reasons:
        reasons.append("Profile details are usable but documentation readiness is not yet well evidenced.")

    return min(score, 10), " ".join(reasons)


def score_reapplication_risk(prior_rejections: int) -> tuple[int, str]:
    if prior_rejections <= 0:
        return 12, "No prior rejection history was provided."
    if prior_rejections == 1:
        return 8, "A prior rejection suggests some unresolved competitiveness risk."
    if prior_rejections == 2:
        return 5, "Multiple prior rejections increase reapplication risk."
    return 2, "Repeated prior rejections materially weaken current readiness."


def build_pr_scoring_rubric(request: AnalyzeRequest) -> dict[str, Any]:
    residency_score, residency_reason = score_years_in_singapore(
        request.years_in_singapore
    )
    employment_score, employment_reason = score_employment_foundation(
        request.pass_type,
        request.monthly_salary,
        request.profession,
    )
    settlement_score, settlement_reason = score_settlement_signals(
        request.marital_status,
        request.spouse_status,
        request.children_count,
        request.family_ties_in_singapore,
    )
    human_capital_score, human_capital_reason = score_human_capital(
        request.education,
        request.language_ability,
    )
    documentation_score, documentation_reason = score_documentation_readiness(
        request.notes,
        request.extra_notes,
        request.profession,
        request.education,
    )
    reapplication_score, reapplication_reason = score_reapplication_risk(
        request.prior_rejections
    )

    preliminary_score = min(
        residency_score
        + employment_score
        + settlement_score
        + human_capital_score
        + documentation_score
        + reapplication_score,
        100,
    )

    return {
        "rubric_name": "singapore_pr_readiness_v1",
        "scoring_principle": (
            "Use PR-specific readiness signals only. Do not use race, religion, "
            "ethnicity, or nationality as scoring variables."
        ),
        "dimensions": [
            {
                "name": "residency_stability",
                "label": "Residency Stability",
                "max_score": 25,
                "score": residency_score,
                "reason": residency_reason,
            },
            {
                "name": "employment_foundation",
                "label": "Employment Foundation",
                "max_score": 28,
                "score": employment_score,
                "reason": employment_reason,
            },
            {
                "name": "settlement_signals",
                "label": "Settlement Signals",
                "max_score": 15,
                "score": settlement_score,
                "reason": settlement_reason,
            },
            {
                "name": "human_capital",
                "label": "Human Capital",
                "max_score": 10,
                "score": human_capital_score,
                "reason": human_capital_reason,
            },
            {
                "name": "documentation_readiness",
                "label": "Documentation Readiness",
                "max_score": 10,
                "score": documentation_score,
                "reason": documentation_reason,
            },
            {
                "name": "reapplication_risk",
                "label": "Reapplication Risk",
                "max_score": 12,
                "score": reapplication_score,
                "reason": reapplication_reason,
            },
        ],
        "preliminary_score": preliminary_score,
        "band_guidance": {
            "low": "0-49: early, weak, or highly incomplete PR profile",
            "moderate": "50-74: plausible PR profile with meaningful gaps or uncertainty",
            "strong": "75-100: well-developed PR profile with multiple positive signals",
        },
    }


def build_scoring_breakdown(
    scoring_rubric: dict[str, Any],
    final_score: int,
    score_adjustment_guidance: dict[str, str] | None = None,
    source_quality: dict[str, Any] | None = None,
) -> dict[str, Any]:
    preliminary_score = scoring_rubric.get("preliminary_score", final_score)
    delta = final_score - preliminary_score
    direction = "none"
    driver = "none"
    guidance = score_adjustment_guidance or {}
    reason = guidance.get(
        "flat_reason",
        "Final score stayed aligned with the rubric baseline.",
    )

    if delta > 0:
        direction = "up"
        driver = "official_evidence"
        reason = guidance.get(
            "up_reason",
            "Official-source evidence modestly strengthened the rubric baseline.",
        )
    elif delta < 0:
        direction = "down"
        driver = "uncertainty"
        reason = guidance.get(
            "down_reason",
            "Uncertainty or weak evidence reduced the rubric baseline modestly.",
        )

    return {
        "rubric_name": scoring_rubric.get("rubric_name", "singapore_pr_readiness_v1"),
        "preliminary_score": preliminary_score,
        "final_score": final_score,
        "score_adjustment": {
            "direction": direction,
            "delta": delta,
            "driver": driver,
            "reason": reason,
        },
        "source_quality": source_quality or {},
        "band_guidance": scoring_rubric.get("band_guidance", {}),
        "dimensions": scoring_rubric.get("dimensions", []),
    }


def summarize_context_quality(context: list[dict[str, Any]]) -> str:
    if not context:
        return "missing"

    substantial_items = 0
    for item in context:
        if not isinstance(item, dict):
            continue
        text_parts = [
            str(item.get("content") or ""),
            str(item.get("text") or ""),
            str(item.get("snippet") or ""),
            str(item.get("summary") or ""),
        ]
        combined = " ".join(part for part in text_parts if part).strip()
        if len(combined) >= 160:
            substantial_items += 1

    if substantial_items >= 2:
        return "strong"
    if substantial_items == 1:
        return "mixed"
    return "thin"


def official_docs_are_supported(official_context: list[dict[str, Any]]) -> bool:
    keywords = (
        "document",
        "documents",
        "supporting",
        "payslip",
        "employer",
        "passport",
        "certificate",
        "application",
        "submit",
    )
    for item in official_context:
        if not isinstance(item, dict):
            continue
        combined = " ".join(
            str(item.get(field) or "")
            for field in ("title", "content", "text", "snippet", "summary", "url")
        ).lower()
        if any(keyword in combined for keyword in keywords):
            return True
    return False


def build_score_adjustment_guidance(
    official_context: list[dict[str, Any]],
    community_context: list[dict[str, Any]],
    retrieval_issue: str | None,
) -> dict[str, str]:
    official_quality = summarize_context_quality(official_context)
    community_quality = summarize_context_quality(community_context)
    docs_supported = official_docs_are_supported(official_context)

    if retrieval_issue:
        return {
            "up_reason": "Official-source support was limited by retrieval issues, so any uplift should stay modest.",
            "down_reason": "Source quality was thin because retrieval issues limited official support and increased uncertainty.",
            "flat_reason": "The score stayed at the rubric baseline because retrieval issues limited source confidence.",
        }

    if official_quality == "strong" and docs_supported:
        return {
            "up_reason": "Official documentation expectations were well supported by the retrieved ICA guidance.",
            "down_reason": "Even with strong official guidance, unresolved profile uncertainty outweighed the supporting evidence.",
            "flat_reason": "Official documentation expectations were clear, but they did not materially change the rubric baseline.",
        }

    if official_quality == "mixed":
        return {
            "up_reason": "Some official guidance supported the profile, but the evidence was only moderately detailed.",
            "down_reason": "Official guidance was only partially supported, which left meaningful uncertainty in the assessment.",
            "flat_reason": "Official guidance was usable but not strong enough to move the rubric baseline.",
        }

    if official_quality in {"thin", "missing"} or community_quality in {"thin", "missing"}:
        return {
            "up_reason": "Any positive adjustment should remain small because source support was limited.",
            "down_reason": "Source quality was thin, so uncertainty reduced confidence in the baseline score.",
            "flat_reason": "Thin source coverage kept the score anchored to the rubric baseline.",
        }

    return {
        "up_reason": "Official-source support modestly strengthened the rubric baseline.",
        "down_reason": "Uncertainty in the retrieved evidence modestly reduced the rubric baseline.",
        "flat_reason": "Final score stayed aligned with the rubric baseline.",
    }


def build_source_quality_summary(
    official_context: list[dict[str, Any]],
    community_context: list[dict[str, Any]],
    retrieval_issue: str | None,
) -> dict[str, Any]:
    official_quality = summarize_context_quality(official_context)
    community_quality = summarize_context_quality(community_context)
    docs_supported = official_docs_are_supported(official_context)

    official_reason = {
        "strong": (
            "Official ICA guidance was strong and detailed."
            if not docs_supported
            else "Official documentation expectations were well supported by retrieved ICA guidance."
        ),
        "mixed": "Some official ICA guidance was available, but detail was only moderate.",
        "thin": "Official source coverage was thin, which limits confidence.",
        "missing": "No official source context was available.",
    }.get(official_quality, "Official source support was unclear.")

    community_reason = {
        "strong": "Community case patterns were plentiful, but still anecdotal.",
        "mixed": "Some community case patterns were available, but coverage was uneven.",
        "thin": "Community evidence was thin and should be treated cautiously.",
        "missing": "No community case context was available.",
    }.get(community_quality, "Community source support was unclear.")

    if retrieval_issue:
        official_reason = "Retrieval issues limited official source support."
        community_reason = "Retrieval issues limited community source support."

    return {
        "official": {
            "level": official_quality if not retrieval_issue else "thin",
            "label": "Official Support",
            "reason": official_reason,
        },
        "community": {
            "level": community_quality if not retrieval_issue else "thin",
            "label": "Community Signals",
            "reason": community_reason,
        },
    }


def build_fallback_response(
    scoring_rubric: dict[str, Any],
    score_adjustment_guidance: dict[str, str],
    source_quality: dict[str, Any],
    official_context: list[dict[str, Any]],
    community_context: list[dict[str, Any]],
    error_note: str,
) -> dict[str, Any]:
    response = dict(FALLBACK_RESPONSE)
    response["scoring_breakdown"] = build_scoring_breakdown(
        scoring_rubric,
        FALLBACK_RESPONSE["readiness_score"],
        score_adjustment_guidance=score_adjustment_guidance,
        source_quality=source_quality,
    )
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
    scoring_rubric = build_pr_scoring_rubric(request)

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

    score_adjustment_guidance = build_score_adjustment_guidance(
        official_context,
        community_context,
        retrieval_issue,
    )
    source_quality = build_source_quality_summary(
        official_context,
        community_context,
        retrieval_issue,
    )

    try:
        analysis_client = OpenAIAnalysisClient()
        result = analysis_client.analyze_profile(
            applicant_profile=build_applicant_profile(request),
            scoring_rubric=scoring_rubric,
            score_adjustment_guidance=score_adjustment_guidance,
            official_context=official_context,
            community_context=community_context,
            extra_notes=request.extra_notes or request.notes,
        )
        result.setdefault(
            "scoring_breakdown",
            build_scoring_breakdown(
                scoring_rubric,
                result["readiness_score"],
                score_adjustment_guidance=score_adjustment_guidance,
                source_quality=source_quality,
            ),
        )
        result["scoring_breakdown"].setdefault("source_quality", source_quality)
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
            scoring_rubric=scoring_rubric,
            score_adjustment_guidance=score_adjustment_guidance,
            source_quality=source_quality,
            official_context=official_context,
            community_context=community_context,
            error_note=error_note,
        )
