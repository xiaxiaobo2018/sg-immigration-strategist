from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


def main() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(env_path)

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5")

    print(f"Loaded env from: {env_path}")
    print(f"Model: {model}")

    if not api_key:
        print("OPENAI_INIT_FAILED")
        print("Missing OPENAI_API_KEY in backend/.env")
        raise SystemExit(1)

    client = OpenAI(api_key=api_key)

    try:
        response = client.responses.create(
            model=model,
            input=(
                "Return a JSON object with keys "
                "\"ping\" and \"message\". Set ping to true."
            ),
        )
    except Exception as exc:
        print("OPENAI_REQUEST_FAILED")
        print(type(exc).__name__)
        print(str(exc))
        raise SystemExit(2)

    output_text = response.output_text.strip()
    print("Raw output:")
    print(output_text[:1000])

    try:
        parsed = json.loads(output_text)
    except Exception:
        print("OPENAI_OK_NON_JSON")
        raise SystemExit(3)

    print("Parsed output:")
    print(json.dumps(parsed, indent=2))
    print("OPENAI_OK")


if __name__ == "__main__":
    main()
