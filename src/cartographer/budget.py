import os
import pathlib
import sys
from collections.abc import Callable, Iterator
from dataclasses import dataclass

SOURCE_SUFFIXES = {".py", ".pyi", ".md", ".rst", ".toml", ".cfg", ".ini", ".yaml", ".yml"}
SKIP_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}

SMALL = "def add(a: int, b: int) -> int:\n    return a + b\n"
LARGE = SMALL * 80


def source_files(root: pathlib.Path) -> Iterator[pathlib.Path]:
    for path in root.rglob("*"):
        if path.suffix not in SOURCE_SUFFIXES or not path.is_file():
            continue
        if SKIP_DIRECTORIES.intersection(path.relative_to(root).parts):
            continue
        yield path


def measure(root: pathlib.Path) -> tuple[int, int]:
    paths = list(source_files(root))
    return len(paths), sum(len(path.read_text(errors="ignore")) for path in paths)


def chars_per_token(count: Callable[[str], int], small: str, large: str) -> float:
    return (len(large) - len(small)) / (count(large) - count(small))


@dataclass
class Meter:
    input_per_million: float = 0.0
    output_per_million: float = 0.0
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0

    def record(self, usage: dict[str, int]) -> None:
        self.calls += 1
        self.input_tokens += usage.get("prompt_tokens", 0)
        self.output_tokens += usage.get("completion_tokens", 0)

    @property
    def dollars(self) -> float:
        billed = (
            self.input_tokens * self.input_per_million
            + self.output_tokens * self.output_per_million
        )
        return billed / 1_000_000

    def __str__(self) -> str:
        return (
            f"{self.calls} calls  in {self.input_tokens}  "
            f"out {self.output_tokens}  ${self.dollars:.4f}"
        )


METER = Meter(
    input_per_million=float(os.environ.get("CARTOGRAPHER_INPUT_PER_MTOK", "0")),
    output_per_million=float(os.environ.get("CARTOGRAPHER_OUTPUT_PER_MTOK", "0")),
)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: python -m cartographer.budget REPO_ROOT")
    from cartographer import agent, budget

    ratio = chars_per_token(agent.prompt_tokens, SMALL, LARGE)
    files, characters = measure(pathlib.Path(sys.argv[1]))
    print(f"files       {files}")
    print(f"characters  {characters}")
    print(f"ratio       {ratio:.2f} characters per token")
    print(f"tokens      {int(characters / ratio)}")
    print(f"calibration {budget.METER}")


if __name__ == "__main__":
    main()
