import os

from openai import OpenAI

PRIMARY_MODEL = "openai/gpt-oss-120b"
FALLBACK_MODEL = "openai/gpt-oss-20b"

_api_key: str | None = None


def _get_api_key() -> str:
    global _api_key
    if _api_key is None:
        _api_key = os.environ.get("OPENROUTER_API_KEY", "")
    return _api_key


def _create_client() -> OpenAI:
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=_get_api_key(),
    )


def call_ai(messages: list[dict]) -> str:
    client = _create_client()

    try:
        response = client.chat.completions.create(
            model=PRIMARY_MODEL,
            messages=messages,
        )
        return response.choices[0].message.content or ""
    except Exception:
        response = client.chat.completions.create(
            model=FALLBACK_MODEL,
            messages=messages,
        )
        return response.choices[0].message.content or ""
