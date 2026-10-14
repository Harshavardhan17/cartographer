import pathlib

from cartographer import budget


def test_calibration_cancels_the_fixed_request_overhead() -> None:
    def counter(text: str) -> int:
        return 11 + len(text) // 4

    assert budget.chars_per_token(counter, "a" * 40, "a" * 4000) == 4.0


def test_measure_skips_vendored_and_generated_trees(tmp_path: pathlib.Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("x = 1\n")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "vendored.py").write_text("y = 2\n")

    files, characters = budget.measure(tmp_path)

    assert files == 1
    assert characters == 6


def test_meter_prices_input_and_output_separately() -> None:
    meter = budget.Meter(input_per_million=1.0, output_per_million=10.0)
    meter.record({"prompt_tokens": 1_000_000, "completion_tokens": 100_000})
    assert meter.dollars == 2.0
