from __future__ import annotations

import json
from pathlib import Path

from dotenv import load_dotenv

try:
    from .services.tinyfish_client import TinyFishClient
except ImportError:
    from services.tinyfish_client import TinyFishClient


DEFAULT_TEST_URLS = ["https://www.ica.gov.sg/reside/PR"]


def summarize_item(item: object) -> dict[str, str]:
    if not isinstance(item, dict):
        return {"type": type(item).__name__, "preview": str(item)[:200]}

    text = " ".join(
        str(item.get(field) or "")
        for field in ("title", "url", "content", "text", "snippet", "summary")
    ).strip()

    return {
        "title": str(item.get("title") or "Untitled"),
        "url": str(item.get("url") or "Unavailable"),
        "preview": text[:240],
    }


def main() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(env_path)

    print(f"Loaded env from: {env_path}")

    try:
        client = TinyFishClient()
    except Exception as exc:
        print("TINYFISH_INIT_FAILED")
        print(str(exc))
        print(
            "If you are following the official TinyFish SDK docs, remove the "
            "TINYFISH_BASE_URL override and either switch this repo to the SDK "
            "path or provide the real HTTP endpoint for the current custom client."
        )
        raise SystemExit(1)

    print("TinyFish SDK client initialized.")

    try:
        results = client.collect_context(
            query="Extract the page title and a one-sentence summary.",
            urls=DEFAULT_TEST_URLS,
            source_type="official",
            limit=1,
        )
    except Exception as exc:
        print("TINYFISH_REQUEST_FAILED")
        print(type(exc).__name__)
        print(str(exc))
        raise SystemExit(2)

    print(f"Returned items: {len(results)}")
    if not results:
        print("No results returned.")
        raise SystemExit(3)

    print("First result summary:")
    print(json.dumps(summarize_item(results[0]), indent=2))
    print("TINYFISH_OK")


if __name__ == "__main__":
    main()
