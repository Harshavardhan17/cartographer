from cartographer.agent import PROMPT


def test_prompt_carries_the_source_and_permits_uncertainty() -> None:
    filled = PROMPT.format(path="src/cartographer/agent.py", source="VALUE = 1")
    assert "VALUE = 1" in filled
    assert "cannot tell" in filled
