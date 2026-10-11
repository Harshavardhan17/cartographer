import pytest

from cartographer import agent


def test_turn_records_both_sides_of_the_exchange(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(agent, "ask", lambda messages: f"saw {len(messages)} messages")
    messages: list[dict[str, str]] = [{"role": "system", "content": agent.SYSTEM}]

    first = agent.turn(messages, "file one")
    second = agent.turn(messages, "file two")

    assert [message["role"] for message in messages] == [
        "system",
        "user",
        "assistant",
        "user",
        "assistant",
    ]
    assert first == "saw 2 messages"
    assert second == "saw 4 messages"
