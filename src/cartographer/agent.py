import json
import os
import pathlib
import sys
from dataclasses import asdict
from typing import Any

import httpx

from cartographer.budget import METER
from cartographer.records import (
    INSTRUCTION,
    REPAIR,
    RESPONSE_FORMAT,
    FileReport,
    InvalidReport,
    parse_report,
)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.environ.get("CARTOGRAPHER_MODEL", "nvidia/nemotron-3.5-super-vl:free")
MAPS = pathlib.Path("maps")

SYSTEM = """You are mapping a repository you have never seen, one file at a time.

Where the file you have been shown does not answer a question, record that as a
finding with low confidence rather than guessing.
"""


def post(
    messages: list[dict[str, str]],
    max_tokens: int | None = None,
    response_format: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"model": MODEL, "messages": messages}
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if response_format is not None:
        payload["response_format"] = response_format
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


def ask(messages: list[dict[str, str]], response_format: dict[str, Any] | None = None) -> str:
    body = post(messages, response_format=response_format)
    return str(body["choices"][0]["message"]["content"])


def prompt_tokens(text: str) -> int:
    body = post([{"role": "user", "content": text}], max_tokens=1)
    return int(body["usage"]["prompt_tokens"])


def turn(
    messages: list[dict[str, str]],
    content: str,
    response_format: dict[str, Any] | None = None,
) -> str:
    messages.append({"role": "user", "content": content})
    reply = ask(messages, response_format)
    messages.append({"role": "assistant", "content": reply})
    return reply


def describe_file(path: pathlib.Path, attempts: int = 3) -> FileReport:
    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM}]
    content = f"{INSTRUCTION}\n--- {path} ---\n{path.read_text()}"
    for attempt in range(1, attempts + 1):
        reply = turn(messages, content, RESPONSE_FORMAT)
        try:
            return parse_report(reply)
        except InvalidReport as error:
            print(f"[repair {attempt}/{attempts}] {error}", file=sys.stderr)
            if attempt == attempts:
                raise
            content = REPAIR.format(error=error)
    raise InvalidReport(f"attempts must be at least 1, got {attempts}")


def main() -> None:
    paths = [pathlib.Path(argument) for argument in sys.argv[1:]]
    if not paths:
        sys.exit("usage: python -m cartographer.agent FILE [FILE ...]")

    MAPS.mkdir(exist_ok=True)
    reports: dict[str, FileReport] = {}
    for path in paths:
        report = describe_file(path)
        reports[str(path)] = report
        print(f"--- {path} ---")
        for found in report.symbols:
            print(f"  {found.kind:11} {found.name:24} line {found.line:<6} {found.role}")
        for note in report.findings:
            print(f"  [{note.confidence:4}] {note.claim}")

    MAPS.joinpath("records.json").write_text(
        json.dumps({name: asdict(report) for name, report in reports.items()}, indent=2)
    )
    print(f"[meter] {METER}", file=sys.stderr)


if __name__ == "__main__":
    main()
