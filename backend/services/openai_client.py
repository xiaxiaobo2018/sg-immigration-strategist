from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from openai import OpenAI


PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "system_prompt.txt"
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")


class OpenAIAnalysisClient:
    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8").strip()

    def analyze_profile(
        self,
        applicant_profile: dict[str, Any],
        scoring_rubric: dict[str, Any] | None = None,
        score_adjustment_guidance: dict[str, str] | None = None,
        official_context: list[dict[str, Any]] | None = None,
        community_context: list[dict[str, Any]] | None = None,
        extra_notes: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "applicant_profile": applicant_profile,
            "scoring_rubric": scoring_rubric or {},
            "score_adjustment_guidance": score_adjustment_guidance or {},
            "official_context": official_context or [],
            "community_context": community_context or [],
            "extra_notes": extra_notes,
            "required_output_schema": {
                "readiness_score": "integer from 0 to 100",
                "eligibility_signal": "low | moderate | strong",
                "scoring_breakdown": {
                    "rubric_name": "string",
                    "preliminary_score": "integer from 0 to 100",
                    "final_score": "integer from 0 to 100",
                    "score_adjustment": {
                        "direction": "up | down | none",
                        "delta": "integer",
                        "driver": "official_evidence | uncertainty | none",
                        "reason": "string",
                    },
                    "source_quality": {
                        "official": {
                            "level": "strong | mixed | thin | missing",
                            "label": "string",
                            "reason": "string",
                        },
                        "community": {
                            "level": "strong | mixed | thin | missing",
                            "label": "string",
                            "reason": "string",
                        },
                    },
                    "band_guidance": {
                        "low": "string",
                        "moderate": "string",
                        "strong": "string",
                    },
                    "dimensions": [
                        {
                            "name": "string",
                            "label": "string",
                            "score": "integer",
                            "max_score": "integer",
                            "reason": "string",
                        }
                    ],
                },
                "official_takeaways": ["string"],
                "community_takeaways": ["string"],
                "top_strengths": ["string"],
                "top_risks": ["string"],
                "missing_documents": ["string"],
                "recommended_actions": ["string"],
                "confidence_notes": ["string"],
                "data_sources_used": {
                    "official_source": "string",
                    "community_source": "string",
                },
                "error_note": None,
            },
        }

        completion = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": (
                        "Analyze the following Singapore PR profile using the "
                        "provided PR-specific scoring rubric as your anchor. "
                        "Use the score_adjustment_guidance to make the adjustment "
                        "reason concrete when the score moves or stays flat. "
                        "You may adjust modestly for strong official evidence or "
                        "major uncertainty, but keep the score aligned with the rubric. "
                        "Return valid JSON only.\n\n"
                        f"{json.dumps(payload, indent=2)}"
                    ),
                },
            ],
        )

        content = completion.choices[0].message.content
        if not content:
            raise ValueError("OpenAI returned an empty response.")

        result = json.loads(content)
        result.setdefault(
            "scoring_breakdown",
            {
                "rubric_name": scoring_rubric.get(
                    "rubric_name",
                    "singapore_pr_readiness_v1",
                ),
                "preliminary_score": scoring_rubric.get(
                    "preliminary_score",
                    result.get("readiness_score", 0),
                ),
                "final_score": result.get("readiness_score", 0),
                "score_adjustment": {
                    "direction": "none",
                    "delta": 0,
                    "driver": "none",
                    "reason": (
                        (score_adjustment_guidance or {}).get(
                            "flat_reason",
                            "Final score stayed aligned with the rubric baseline.",
                        )
                    ),
                },
                "source_quality": {},
                "band_guidance": scoring_rubric.get("band_guidance", {}),
                "dimensions": scoring_rubric.get("dimensions", []),
            },
        )
        result.setdefault(
            "data_sources_used",
            {
                "official_source": (
                    official_context[0].get("title")
                    or official_context[0].get("url")
                    if official_context and isinstance(official_context[0], dict)
                    else "ICA PR guidance"
                ),
                "community_source": (
                    community_context[0].get("title")
                    or community_context[0].get("url")
                    if community_context and isinstance(community_context[0], dict)
                    else "Reddit PR discussion thread"
                ),
            },
        )
        result.setdefault("error_note", None)
        return result
