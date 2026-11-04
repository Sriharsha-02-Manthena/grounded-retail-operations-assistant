"""Meta Model API client, used ONLY when a key is configured.

Configuration (environment variables, no keys are stored in this repo):
  MODEL_API_KEY           - required to make any Meta call, per the
                            official Meta Model API docs. Not set by
                            default. This is checked FIRST.
  META_MODEL_API_KEY      - fallback, accepted for backwards
                            compatibility with the earlier demo build.
  META_MODEL_API_BASE_URL - default https://api.meta.ai/v1 (Meta Model API).
  META_MODEL_NAME         - default muse-spark-1.3 (Muse Spark).

Behaviour:
  - If neither MODEL_API_KEY nor META_MODEL_API_KEY is set,
    generate_answer() returns None and the app falls back to extractive
    cited answers. The response then says so explicitly; it never claims
    a Meta model generated an answer it did not.
  - If a key is set, the client POSTs an OpenAI-compatible chat completion
    with the retrieved passages as context and an instruction to answer
    ONLY from those passages. Network/API errors are returned as an error
    string (not raised into a fake answer), and the app falls back too.
  - This module has not been run against a live key in this demo build,
    so a live Meta call is untested here. See README.md.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

BASE_URL = os.environ.get("META_MODEL_API_BASE_URL", "https://api.meta.ai/v1")
MODEL_NAME = os.environ.get("META_MODEL_NAME", "muse-spark-1.3")


def get_api_key() -> str | None:
    """Official name first, legacy name as fallback. Never logged."""
    return os.environ.get("MODEL_API_KEY") or os.environ.get("META_MODEL_API_KEY")


def is_configured() -> bool:
    return bool(get_api_key())


def generate_answer(question: str, passages: list[dict]) -> tuple[str | None, str | None]:
    """Return (text, error). text is None when no call was made or it failed."""
    api_key = get_api_key()
    if not api_key:
        return None, "no_key"
    context = "\n\n".join(
        f"[{p['doc']} - {p['section']}] {p['text']}" for p in passages
    )
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Answer only using the passages below. "
                    "Do not add facts that are not in the passages. "
                    "If the passages do not answer the question, say so."
                ),
            },
            {
                "role": "user",
                "content": f"Passages:\n{context}\n\nQuestion: {question}",
            },
        ],
    }
    req = urllib.request.Request(
        f"{BASE_URL.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        text = body["choices"][0]["message"]["content"]
        return text, None
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError,
            IndexError, ValueError) as exc:
        return None, f"meta_call_failed: {exc}"
