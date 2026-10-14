import json
import os
import pathlib
import sys
from typing import Any

import httpx

from cartographer.budget import METER

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.environ.get("CARTOGRAPHER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")
TRANSCRIPT = pathlib.Path("transcript.json")

SYSTEM = """You are mapping a repository you have never seen, one file at a time.

Refer back to files you have already been shown, by name. Where the files you
have seen do not answer a question, answer that you cannot tell.
"""


def post(messages: list[dict[str, str]], max_tokens: int | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"model": MODEL, "messages": messages}
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    response = httpx.post(
        OPENROUTER_URL,
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
        json=payload,
        timeout=120.0,
    )
    response.raise_for_status()
    body: dict[str, Any] = response.json()
    METER.record(body.get("usage") or {})
    return body


def ask(messages: list[dict[str, str]]) -> str:
    body = post(messages)
    return str(body["choices"][0]["message"]["content"])


def prompt_tokens(text: str) -> int:
    body = post([{"role": "user", "content": text}], max_tokens=1)
    return int(body["usage"]["prompt_tokens"])


def turn(messages: list[dict[str, str]], content: str) -> str:
    messages.append({"role": "user", "content": content})
    reply = ask(messages)
    messages.append({"role": "assistant", "content": reply})
    return reply


def main() -> None:
    paths = [pathlib.Path(argument) for argument in sys.argv[1:]]
    if not paths:
        sys.exit("usage: python -m cartographer.agent FILE [FILE ...]")

    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM}]
    for path in paths:
        print(turn(messages, f"--- {path} ---\n{path.read_text()}"))
    print(turn(messages, "Which of these files would you read first, and why?"))

    TRANSCRIPT.write_text(json.dumps(messages, indent=2))
    print(f"\n{len(messages)} messages in {TRANSCRIPT}", file=sys.stderr)
    print(f"[meter] {METER}", file=sys.stderr)


if __name__ == "__main__":
    main()
