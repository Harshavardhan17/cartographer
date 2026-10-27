import json

import pytest

from cartographer import records

VALID = {
    "symbols": [
        {
            "name": "measure",
            "kind": "function",
            "file": "src/cartographer/budget.py",
            "line": 46,
            "role": "counts files and characters under a root",
        }
    ],
    "findings": [
        {
            "claim": "the module never makes a network call",
            "evidence": "no import of httpx anywhere in the file",
            "confidence": "high",
        }
    ],
}


def test_parse_report_produces_typed_records() -> None:
    report = records.parse_report(json.dumps(VALID))

    assert report.symbols[0] == records.Symbol(
        name="measure",
        kind="function",
        file="src/cartographer/budget.py",
        line=46,
        role="counts files and characters under a root",
    )
    assert report.findings[0].confidence == "high"


def test_parse_report_survives_a_markdown_fence() -> None:
    fenced = "```json\n" + json.dumps(VALID) + "\n```"

    assert records.parse_report(fenced).symbols[0].name == "measure"


def test_parse_report_names_the_missing_field() -> None:
    broken = json.loads(json.dumps(VALID))
    del broken["symbols"][0]["line"]

    with pytest.raises(records.InvalidReport, match="'line'"):
        records.parse_report(json.dumps(broken))


def test_parse_report_rejects_a_line_number_sent_as_a_string() -> None:
    broken = json.loads(json.dumps(VALID))
    broken["symbols"][0]["line"] = "46"

    with pytest.raises(records.InvalidReport, match="must be int, got str"):
        records.parse_report(json.dumps(broken))


def test_parse_report_rejects_a_kind_outside_the_enum() -> None:
    broken = json.loads(json.dumps(VALID))
    broken["symbols"][0]["kind"] = "helper"

    with pytest.raises(records.InvalidReport, match="not one of"):
        records.parse_report(json.dumps(broken))


def test_parse_report_rejects_prose() -> None:
    with pytest.raises(records.InvalidReport, match="not JSON"):
        records.parse_report("This file defines a measure function.")


def test_the_schema_forbids_extra_keys_at_every_level() -> None:
    assert records.REPORT_SCHEMA["additionalProperties"] is False
    assert records.SYMBOL_SCHEMA["additionalProperties"] is False
    assert set(records.SYMBOL_SCHEMA["required"]) == {"name", "kind", "file", "line", "role"}
