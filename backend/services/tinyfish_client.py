from __future__ import annotations

import json
import os
from typing import Any

from tinyfish import TinyFish
from tinyfish.agent.types import BrowserProfile, ProxyConfig


OFFICIAL_ICA_URL = "https://www.ica.gov.sg/reside/PR"
OFFICIAL_EPR_URL = "https://eservices.ica.gov.sg/esvclandingpage/epr"
COMMUNITY_FORUM_URL = (
    "https://www.reddit.com/r/askSingapore/comments/1k3m7om/"
    "how_long_does_it_take_to_get_pr_reasons_for/"
)
COMMUNITY_FORUM_URL_2 = "https://forum.singaporeexpats.com/viewforum.php?f=78"


class TinyFishConfigError(ValueError):
    pass


class TinyFishRequestError(RuntimeError):
    pass


def merge_official_context_items(
    official_context: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if len(official_context) <= 1:
        return official_context

    merged_points: list[str] = []
    merged_summaries: list[str] = []
    merged_urls: list[str] = []

    for item in official_context:
        if not isinstance(item, dict):
            continue
        summary = str(item.get("summary") or "").strip()
        if summary and summary not in merged_summaries:
            merged_summaries.append(summary)

        url = str(item.get("url") or "").strip()
        if url and url not in merged_urls:
            merged_urls.append(url)

        for point in item.get("key_points") or []:
            point_text = str(point).strip()
            if point_text and point_text not in merged_points:
                merged_points.append(point_text)

    merged_summary = " ".join(merged_summaries).strip()
    merged_content = "\n".join(
        [part for part in [merged_summary, *merged_points] if part]
    ).strip()

    return [
        {
            "title": "ICA PR and e-PR Combined Guidance",
            "url": " | ".join(merged_urls),
            "source_type": "official",
            "summary": merged_summary or "Combined official ICA guidance from multiple PR pages.",
            "key_points": merged_points,
            "content": merged_content,
            "merged_from": len(official_context),
            "sources": official_context,
        }
    ]


class TinyFishClient:
    def __init__(
        self,
        api_key: str | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("TINYFISH_API_KEY")
        if not self.api_key:
            raise TinyFishConfigError("Missing TINYFISH_API_KEY environment variable.")

        self.client = TinyFish(api_key=self.api_key)

    def build_goal(self, query: str, source_type: str) -> str:
        if source_type == "official":
            return (
                "Visit the provided ICA page and extract only page-grounded Singapore PR "
                "information that is clearly visible on that page. Focus on three things: "
                "eligibility criteria, required supporting documents, and application method "
                'or process. Return JSON only with keys "title", "eligibility", '
                '"documents", and "application_process". Each of the last three keys should '
                "be an array of short strings. If the page is thin, blocked, or does not "
                "clearly contain one of those sections, return an empty array for that key "
                f"and briefly reflect the limitation in the title if needed. Task: {query}."
            )

        if source_type == "community":
            return (
                "Visit the provided community page and extract only page-grounded Singapore "
                "PR anecdotal case patterns. Focus on approval concerns, rejection worries, "
                "and recurring practical advice discussed by applicants. Return JSON only "
                'with keys "title", "summary", and "key_points". "summary" should be 1 to '
                '2 sentences and "key_points" should contain at most 3 short strings. '
                "If the page is blocked, unrelated, or too thin, return a brief limitation "
                f'in "summary" and an empty "key_points" array. Task: {query}.'
            )

        return (
            f"Visit the provided page URL and extract concise {source_type} context "
            "for a Singapore PR readiness tool. Use only information visible on that "
            "page. If the page is blocked, unrelated, or content is too thin, return "
            'JSON with a best-effort "title", a brief "summary" explaining the '
            'limitation, and an empty "key_points" array. '
            f"Task: {query}. Return JSON only with keys "
            '"title", "summary", and "key_points". '
            '"summary" should be 1 to 2 sentences and page-grounded. '
            '"key_points" should contain at most 3 short strings.'
        )

    def get_browser_profile(self, source_type: str) -> BrowserProfile:
        if source_type == "community":
            return BrowserProfile.STEALTH
        return BrowserProfile.LITE

    def get_proxy_config(self, source_type: str) -> ProxyConfig:
        if source_type == "community":
            return ProxyConfig(enabled=True)
        return ProxyConfig(enabled=False)

    def start_live_preview(
        self,
        *,
        url: str,
        query: str,
        source_type: str = "general",
    ) -> dict[str, Any]:
        browser_profile = self.get_browser_profile(source_type)
        proxy_config = self.get_proxy_config(source_type)

        try:
            with self.client.agent.stream(
                goal=self.build_goal(query, source_type),
                url=url,
                browser_profile=browser_profile,
                proxy_config=proxy_config,
            ) as stream:
                for event in stream:
                    if getattr(event, "type", None) == "STREAMING_URL":
                        return {
                            "run_id": event.run_id,
                            "streaming_url": event.streaming_url,
                            "url": url,
                            "source_type": source_type,
                        }
                    if getattr(event, "type", None) == "COMPLETE":
                        error_message = (
                            event.error.message
                            if getattr(event, "error", None) is not None
                            else "TinyFish run completed before a streaming URL was provided."
                        )
                        raise TinyFishRequestError(
                            f"TinyFish preview failed for {url}: {error_message}"
                        )
        except Exception as exc:
            raise TinyFishRequestError(
                f"TinyFish preview failed for {url}: {exc}"
            ) from exc

        raise TinyFishRequestError(
            f"TinyFish preview failed for {url}: no streaming URL was returned."
        )

    def normalize_result(
        self,
        *,
        url: str,
        source_type: str,
        response_data: Any,
    ) -> dict[str, Any]:
        result = response_data.result
        if not isinstance(result, dict):
            result = {"summary": json.dumps(result) if result is not None else ""}

        title = str(result.get("title") or response_data.run_id or url)
        if source_type == "official":
            eligibility = result.get("eligibility")
            documents = result.get("documents")
            application_process = result.get("application_process")
            eligibility = eligibility if isinstance(eligibility, list) else []
            documents = documents if isinstance(documents, list) else []
            application_process = (
                application_process if isinstance(application_process, list) else []
            )
            key_points = [
                *[str(point) for point in eligibility if str(point).strip()],
                *[f"Document: {point}" for point in documents if str(point).strip()],
                *[
                    f"Process: {point}"
                    for point in application_process
                    if str(point).strip()
                ],
            ]
            summary = " ".join(
                [
                    "Eligibility, documents, and application flow were extracted from the ICA page."
                    if key_points
                    else "The ICA page returned limited structured detail."
                ]
            )
        else:
            summary = str(result.get("summary") or "")
            key_points = result.get("key_points")
            if not isinstance(key_points, list):
                key_points = []

        error = None
        if response_data.error is not None:
            error = {
                "message": response_data.error.message,
                "category": response_data.error.category,
                "retry_after": response_data.error.retry_after,
                "help_url": response_data.error.help_url,
                "help_message": response_data.error.help_message,
            }

        return {
            "title": title,
            "url": url,
            "source_type": source_type,
            "summary": summary,
            "key_points": [str(point) for point in key_points if str(point).strip()],
            "content": "\n".join(
                [summary] + [str(point) for point in key_points if str(point).strip()]
            ).strip(),
            "run_id": response_data.run_id,
            "status": response_data.status,
            "num_of_steps": response_data.num_of_steps,
            "error": error,
        }

    def collect_context(
        self,
        query: str,
        urls: list[str] | None = None,
        source_type: str = "general",
        limit: int = 1,
    ) -> list[dict[str, Any]]:
        target_urls = (urls or [])[:limit]
        if not target_urls:
            return []

        results: list[dict[str, Any]] = []
        failures: list[str] = []
        browser_profile = self.get_browser_profile(source_type)
        proxy_config = self.get_proxy_config(source_type)

        for url in target_urls:
            try:
                response = self.client.agent.run(
                    goal=self.build_goal(query, source_type),
                    url=url,
                    browser_profile=browser_profile,
                    proxy_config=proxy_config,
                )

                if response.status != "COMPLETED":
                    error_message = (
                        response.error.message if response.error else "Unknown TinyFish failure"
                    )
                    raise TinyFishRequestError(f"TinyFish run failed for {url}: {error_message}")

                results.append(
                    self.normalize_result(
                        url=url,
                        source_type=source_type,
                        response_data=response,
                    )
                )
            except Exception as exc:
                failures.append(f"{url}: {exc}")

        if results:
            return results
        if failures:
            raise TinyFishRequestError("; ".join(failures))

        return []


def get_default_official_urls() -> list[str]:
    return [OFFICIAL_EPR_URL, OFFICIAL_ICA_URL]


def get_default_community_urls() -> list[str]:
    return [COMMUNITY_FORUM_URL_2]
