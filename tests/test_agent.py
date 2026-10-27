import json
import pathlib

import pytest

from cartographer import agent, records

GOOD = json.dumps({"symbols": [], "findings": []})
BAD = "Sure! Here is what I found: the file defines two functions."


def test_describe_file_repairs_an_unparseable_reply(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    replies = [BAD, GOOD]
    sent: list[list[dict[str, str]]] = []

    def fake_ask(
        messages: list[dict[str, str]], response_format: dict[str, object] | None = None
    ) -> str:
        sent.append([dict(message) for message in messages])
        return replies.pop(0)

    monkeypatch.setattr(agent, "ask", fake_ask)
    target = tmp_path / "sample.py"
    target.write_text("VALUE = 1\n")

    report = agent.describe_file(target)

    assert report == records.FileReport(symbols=[], findings=[])
    assert len(sent) == 2
    assert sent[1][-2]["content"] == BAD
    assert "not JSON" in sent[1][-1]["content"]


def test_describe_file_gives_up_after_the_last_attempt(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    calls = 0

    def always_bad(
        messages: list[dict[str, str]], response_format: dict[str, object] | None = None
    ) -> str:
        nonlocal calls
        calls += 1
        return BAD

    monkeypatch.setattr(agent, "ask", always_bad)
    target = tmp_path / "sample.py"
    target.write_text("VALUE = 1\n")

    with pytest.raises(records.InvalidReport):
        agent.describe_file(target, attempts=2)

    assert calls == 2
