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
        official_context: list[dict[str, Any]] | None = None,
        community_context: list[dict[str, Any]] | None = None,
        extra_notes: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "applicant_profile": applicant_profile,
            "official_context": official_context or [],
            "community_context": community_context or [],
            "extra_notes": extra_notes,
            "required_output_schema": {
                "readiness_score": "integer from 0 to 100",
                "eligibility_signal": "low | moderate | strong",
                "top_strengths": ["string"],
                "top_risks": ["string"],
                "missing_documents": ["string"],
                "recommended_actions": ["string"],
                "confidence_notes": ["string"],
                "source_context": {
                    "official_sources": ["object"],
                    "community_sources": ["object"],
                },
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
                        "Analyze the following Singapore immigration profile and "
                        "return valid JSON only.\n\n"
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
            "data_sources_used",
            {
                "official_source": (
                    official_context[0].get("title")
                    if official_context and isinstance(official_context[0], dict)
                    else "ICA requirements page"
                ),
                "community_source": (
                    community_context[0].get("title")
                    if community_context and isinstance(community_context[0], dict)
                    else "Public applicant discussion thread"
                ),
            },
        )
        result.setdefault("error_note", None)
        return result
