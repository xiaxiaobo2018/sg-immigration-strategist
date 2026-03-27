from __future__ import annotations

import os
from typing import Any

import httpx


DEFAULT_BASE_URL = os.getenv(
    "TINYFISH_BASE_URL",
    os.getenv("TINYFISH_API_URL", "https://api.tinyfish.ai"),
)


class TinyFishConfigError(ValueError):
    pass


class TinyFishClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 20.0,
    ) -> None:
        self.api_key = api_key or os.getenv("TINYFISH_API_KEY")
        if not self.api_key:
            raise TinyFishConfigError("Missing TINYFISH_API_KEY environment variable.")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def collect_context(
        self,
        query: str,
        urls: list[str] | None = None,
        source_type: str = "general",
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        payload = {
            "query": query,
            "urls": urls or [],
            "source_type": source_type,
            "limit": limit,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/extract",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("results", "items", "data"):
                value = data.get(key)
                if isinstance(value, list):
                    return value
            return [data]
        return []
