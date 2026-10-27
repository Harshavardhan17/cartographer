import json
import os
from dataclasses import dataclass
from typing import Any, TypeVar

KINDS = ("module", "class", "function", "constant", "entrypoint")
CONFIDENCES = ("high", "low")

T = TypeVar("T")


class InvalidReport(ValueError):
    pass


@dataclass(frozen=True)
class Symbol:
    name: str
    kind: str
    file: str
    line: int
    role: str


@dataclass(frozen=True)
class Finding:
    claim: str
    evidence: str
    confidence: str


@dataclass
class FileReport:
    symbols: list[Symbol]
    findings: list[Finding]


def json_object(properties: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


SYMBOL_SCHEMA = json_object(
    {
        "name": {"type": "string"},
        "kind": {"type": "string", "enum": list(KINDS)},
        "file": {"type": "string"},
        "line": {"type": "integer"},
        "role": {"type": "string"},
    }
)

FINDING_SCHEMA = json_object(
    {
        "claim": {"type": "string"},
        "evidence": {"type": "string"},
        "confidence": {"type": "string", "enum": list(CONFIDENCES)},
    }
)

REPORT_SCHEMA = json_object(
    {
        "symbols": {"type": "array", "items": SYMBOL_SCHEMA},
        "findings": {"type": "array", "items": FINDING_SCHEMA},
    }
)

STRUCTURED = os.environ.get("CARTOGRAPHER_STRUCTURED", "1") != "0"

RESPONSE_FORMAT: dict[str, Any] | None = (
    {
        "type": "json_schema",
        "json_schema": {"name": "file_report", "strict": True, "schema": REPORT_SCHEMA},
    }
    if STRUCTURED
    else None
)

INSTRUCTION = """Return one JSON object with exactly two keys, and nothing else.

"symbols": the definitions in this file a newcomer has to understand. Each one has
name, kind (module, class, function, constant or entrypoint), file (the path exactly
as it was given to you), line (a number), and role (one sentence on why it matters).

"findings": what you concluded about the file. Each one has claim, evidence (quote
or name the line you got it from), and confidence ("high" if the file shows it,
"low" if you are inferring it).

Report only what this file shows. Two empty lists are a valid answer.
"""

REPAIR = """That response was rejected: {error}

Send the corrected JSON object only. No prose, no code fence, no explanation.
"""

FENCE = "```"


def strip_fences(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith(FENCE):
        return stripped
    body = stripped[len(FENCE) :]
    if body.startswith("json"):
        body = body[len("json") :]
    return body.rsplit(FENCE, 1)[0].strip()


def require(payload: dict[str, Any], key: str, expected: type[T]) -> T:
    if key not in payload:
        raise InvalidReport(f"missing required field {key!r}")
    value: object = payload[key]
    if isinstance(value, bool) or not isinstance(value, expected):
        raise InvalidReport(
            f"field {key!r} must be {expected.__name__}, got {type(value).__name__}"
        )
    return value


def one_of(value: str, allowed: tuple[str, ...], field: str) -> str:
    if value not in allowed:
        raise InvalidReport(f"{field} {value!r} is not one of {', '.join(allowed)}")
    return value


def to_symbol(item: Any) -> Symbol:
    if not isinstance(item, dict):
        raise InvalidReport(f"each symbol must be an object, got {type(item).__name__}")
    return Symbol(
        name=require(item, "name", str),
        kind=one_of(require(item, "kind", str), KINDS, "kind"),
        file=require(item, "file", str),
        line=require(item, "line", int),
        role=require(item, "role", str),
    )


def to_finding(item: Any) -> Finding:
    if not isinstance(item, dict):
        raise InvalidReport(f"each finding must be an object, got {type(item).__name__}")
    return Finding(
        claim=require(item, "claim", str),
        evidence=require(item, "evidence", str),
        confidence=one_of(require(item, "confidence", str), CONFIDENCES, "confidence"),
    )


def load_object(text: str) -> dict[str, Any]:
    try:
        payload = json.loads(strip_fences(text))
    except json.JSONDecodeError as error:
        raise InvalidReport(f"not JSON: {error}") from error
    if not isinstance(payload, dict):
        raise InvalidReport(f"top level must be an object, got {type(payload).__name__}")
    return payload


def parse_report(text: str) -> FileReport:
    payload = load_object(text)
    return FileReport(
        symbols=[to_symbol(item) for item in require(payload, "symbols", list)],
        findings=[to_finding(item) for item in require(payload, "findings", list)],
    )
