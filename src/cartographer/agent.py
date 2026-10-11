import json
import os
import pathlib
import sys

import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.environ.get("CARTOGRAPHER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")
TRANSCRIPT = pathlib.Path("transcript.json")

SYSTEM = """You are mapping a repository you have never seen, one file at a time.

Refer back to files you have already been shown, by name. Where the files you
have seen do not answer a question, answer that you cannot tell.
"""

def ask(messages: list[dict[str, str]]) -> str:
    response = httpx.post(
        OPENROUTER_URL,
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
        json={"model": MODEL, "messages": messages},
        timeout=120.0,
    )
    response.raise_for_status()
    body = response.json()
    return str(body["choices"][0]["message"]["content"])


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


if __name__ == "__main__":
    main()
