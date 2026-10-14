# Day 03: Your repo does not fit in the context window. Now what?

Dev notes for this day's post: [read the post](https://harshakatkam.dev/a-repo-does-not-fit-in-context).
Step numbers follow the full build guide; steps only the repository owner needs, such as publishing to GitHub, are left out. New here? Start with [how to use these notes](README.md).

---

**Today's build:** the tape measure and the meter

Starting point: yesterday's `src/cartographer/agent.py` with `ask(messages)`,
`turn(messages, content)` and a transcript dumped to `transcript.json`. It reads whatever
files you name on the command line and remembers them. Nothing in the project knows what
any of that costs.

Today: a new pure module `budget.py` that measures a repository and prices a run, and a
small refactor of `agent.py` so every response's `usage` block is recorded automatically.
No new dependencies.

Two words you need today. A **token** is a chunk of text, often a short word or part of a
longer one; models read, write and bill in tokens, not characters. The **context window**
is the most tokens one request can hold, your messages and the reply together.

Time: about an hour, plus a few minutes of calibration calls.

**Readiness check.** Before anything else, confirm the target Day 00 cloned is still in
place:

    echo "$CARTOGRAPHER_TARGET"                    # ends in /workspace/personal/targets/click
    git -C "$CARTOGRAPHER_TARGET" rev-parse HEAD   # 8b19813f2bfca99f1018a587a8cf54fc959f2e5d

An empty first line means this terminal has not loaded your shell profile: run
`source ~/.zshrc` (or `~/.bashrc`). An error or a different SHA from the second means the
clone is missing or is not click 8.5.0: redo Day 00's Step 14.

## Files you will touch today

| File | New or edited | What it is for |
|---|---|---|
| `src/cartographer/budget.py` | New | Counts a repository's source files and characters, converts characters to tokens, and keeps a running meter of tokens and cost |
| `src/cartographer/agent.py` | Edited | Splits the HTTP call into `post` (which records token usage in the meter) and `ask`; adds `prompt_tokens`; prints the meter |
| `tests/test_budget.py` | New | Three offline tests: the calibration maths, the directory skip list, and the pricing |
| `docs/measurements.md` | New | Where the measured size of each test repository is recorded, with its commit |

## Commands and tools today

| Command | What it does |
|---|---|
| `echo "$CARTOGRAPHER_TARGET"` | Readiness check, part one: prints the target's path |
| `git -C "$CARTOGRAPHER_TARGET" rev-parse HEAD` | Readiness check, part two: prints the target's commit |
| `cd ~/workspace/personal/cartographer` | Moves to the repo root |
| `git checkout main` | Switches to the main branch |
| `git checkout -b day-03-token-budget` | Creates today's branch and switches to it |
| `git branch --show-current` | Prints the branch you are on |
| `uv run python -c "from cartographer.budget import measure; ..."` | Measures this repository with no network call |
| `uv run mypy src` | Type-checks the package |
| `uv run python -c "import cartographer.agent"` | Imports the agent, proving there is no import cycle |
| `uv run pytest -q` | Runs the tests |
| `uv run python -m cartographer.budget .` | Calibrates characters per token with two tiny requests, then sizes this repository |
| `git -C "$CARTOGRAPHER_TARGET" rev-parse HEAD` | Prints the target's commit, to record beside its numbers |
| `uv run python -m cartographer.budget "$CARTOGRAPHER_TARGET"` | Sizes the target in files, characters and estimated tokens |
| `git rev-parse HEAD` | Prints this repository's own commit, for its row |
| `mkdir -p docs` | Creates the `docs/` folder |
| `uv run ruff check . && uv run ruff format .` | Lints, then formats every file |
| `git add -A` | Stages every new and changed file |
| `git commit -m "..."` | Records today's work as one commit |
| `git checkout main` | Switches back to the main branch |
| `git merge day-03-token-budget` | Brings today's branch onto `main` |
| `git tag day-03` | Bookmarks the finished day |
| `git log --oneline -3` | Shows the last three commits |

New tools today: none

## Step 1 — Start a branch for today

**Where:** the repo root, `~/workspace/personal/cartographer`.
**Why this step exists:** one branch per day, merged the same day.

**Run this:**

    cd ~/workspace/personal/cartographer
    git checkout main
    git checkout -b day-03-token-budget

**What each part does:** `cd` moves to the repo root; `git checkout main` switches to the
main branch, which holds every finished day; `git checkout -b day-03-token-budget` creates today's
branch from it and switches to it (`-b` is "create, then switch").

**Check it:** `git branch --show-current` prints `day-03-token-budget`.

## Step 2 — Write `src/cartographer/budget.py`

**Where:** `src/cartographer/budget.py` — new file.
**Why this file exists:** pure module. It knows about the filesystem and about arithmetic,
and nothing about HTTP. That keeps every number it produces testable without a network.

**Add this code:**

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

**What each part does:**

*Imports.* `os` reads the price variables, `pathlib` walks folders, `sys` reads the command
line. `Callable` and `Iterator` (from `collections.abc`) are only used in type hints: "a
function" and "something you can loop over". `dataclass` generates the boilerplate for a
class that mostly holds data.

*The two sets.* `SOURCE_SUFFIXES` lists the file extensions that count as something a
person wrote and a newcomer might read: Python, stubs, docs, and configuration.
`SKIP_DIRECTORIES` lists folders that are never the project's own code: git's history,
virtual environments, JavaScript dependencies, and the caches Python, mypy, pytest and ruff
write. Curly braces make them **sets**, which are fast to check membership against.
`SKIP_DIRECTORIES` is written one entry per line, with a comma after the last, because that
is how `ruff format` lays out a collection too long for one line.

*The calibration samples.* `SMALL` is a two-line Python function as a string (`\n` is a
line break). `LARGE` is the same text repeated 80 times. They are realistic code, because
code splits into tokens differently from prose, and very different in size, which is what
the subtraction below needs.

*`source_files(root)`.* A **generator**: a function that hands back results one at a time
with `yield` instead of building a list.

- `root.rglob("*")` walks every file and folder under `root`, recursively.
- `if path.suffix not in SOURCE_SUFFIXES or not path.is_file(): continue` skips anything
  whose extension is not on the list, and anything that is not a regular file, such as a
  folder whose name happens to end in `.md` (`continue` jumps to the next item).
- `path.relative_to(root).parts` is the list of folder names between `root` and the file.
  `SKIP_DIRECTORIES.intersection(...)` compares the set against each of them. Any overlap
  means the file lives somewhere under, say, `.venv`, so it is skipped. Only the part below
  `root` is checked, so a repository that itself sits inside a folder called `venv` is
  still measured.
- `yield path` hands back a file that passed both checks.

*`measure(root)`.* Collects the files into a list, then returns two numbers: how many there
are, and the total number of characters across them. `read_text(errors="ignore")` drops
any bytes that are not valid text instead of crashing on one odd file.

*`chars_per_token(count, small, large)`.* The two-point calibration, in one line. `count`
is any function that takes text and returns a token count; the real one asks the server.
Every request carries a fixed overhead of tokens you did not write (the chat template the
server wraps your message in). Counting two samples and subtracting cancels that overhead:
`(len(large) - len(small))` is the extra characters, `(count(large) - count(small))` is the
extra tokens, and their ratio is characters per token for this model.

*`Meter`.* A running total of what the run has used.

- `@dataclass` writes the `__init__` for you from the field list, so
  `Meter(input_per_million=1.0)` works and every other field starts at its default.
- `input_per_million` and `output_per_million` are prices in dollars per million tokens.
  They are separate because providers charge differently for the two directions:
  **input** (prompt) tokens are what you send, **output** (completion) tokens are what the
  model writes.
- `calls`, `input_tokens`, `output_tokens` are the counters.
- `record(usage)` takes the `usage` block every response carries and adds it in:
  `prompt_tokens` to input, `completion_tokens` to output. `.get(key, 0)` treats a missing
  field as zero instead of crashing.
- `@property` makes `dollars` read like a field (`meter.dollars`, no parentheses) while
  being computed fresh each time: tokens times price per million, divided by a million.
  `1_000_000` is just a million; underscores make long numbers readable.
- `__str__` decides what `print(meter)` shows: calls, input, output and dollars to four
  decimal places (`:.4f`).

*`METER`.* The one meter the whole program shares. The prices come from two environment
variables and default to `"0"`.

*`main()`.*

- `len(sys.argv) != 2` insists on exactly one argument, the repository folder.
- `from cartographer import agent, budget` is inside the function on purpose (see the third
  decision below). It imports `agent` for its token counter, and, oddly, this very module,
  `budget`, by its package name; Step 5's check explains why that second import is needed.
- `ratio = chars_per_token(agent.prompt_tokens, SMALL, LARGE)` makes two real requests and
  computes the ratio.
- `measure(...)` walks the repository.
- The `print` lines report files, characters, the ratio to two decimals, and the estimated
  tokens (`characters / ratio`, rounded down by `int`), then `budget.METER`, the meter
  those two requests were recorded on.

Three decisions to be able to defend:

- **Prices come from the environment, never from source.** Published rates change and a
  literal in a repo becomes a lie without anyone editing it. Zero is the right default:
  on a free model the dollars really are zero, and the token counts are still true.
- **`chars_per_token` takes the counter as an argument.** That keeps `budget.py` free of
  HTTP, makes it testable with no network, and lets you calibrate a different backend
  later without touching it.
- **The imports are inside `main`.** `agent.py` imports `METER` from here, so a
  module-level import back into `agent` would be a cycle. This is the only
  place `budget` needs the network, so the local import is the smaller compromise.

**Check it:**

    uv run python -c "from cartographer.budget import measure; print(measure(__import__('pathlib').Path('.')))"

It prints two numbers for this repository: a file count around ten and a character count
in the thousands. No request is made.

## Step 3 — Refactor `src/cartographer/agent.py`

**Where:** `src/cartographer/agent.py` — edit to an existing file.
**Why this change exists:** every response carries a `usage` block saying how many tokens
it counted. Routing every request through one function that records it means nothing can
bypass the meter.

Split the HTTP call in two: `post` returns the whole body and records usage; `ask` keeps
its old signature on top of it. Add `prompt_tokens`.

The block below holds every new piece together; they go in four places in the file:

1. `from typing import Any` goes with the standard-library imports, after `import sys`.
2. `from cartographer.budget import METER` goes after `import httpx`, separated from it by a
   blank line (the project's own imports come last).
3. Find the existing `ask` function and replace it with `post` followed by the new `ask`.
4. `prompt_tokens` goes straight after the new `ask`, before `turn`.

**Add this code:**

    from typing import Any

    from cartographer.budget import METER

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

**What each part does:**

*The imports.* `Any` is the type-hint for "any value at all", needed because a JSON
response can hold anything. `METER` is the shared meter from Step 2.

*`post(messages, max_tokens=None)`.* Yesterday's `ask`, minus the last line, plus two
things.

- `max_tokens: int | None = None` is an optional cap on how many tokens the model may write.
  `int | None` means "an integer, or nothing"; the default `None` means "no cap".
- `payload` is the request body, built as a dictionary first so a field can be added
  conditionally. `dict[str, Any]` tells mypy its values can be of mixed types.
- `if max_tokens is not None: payload["max_tokens"] = max_tokens` sends the cap only when
  one was asked for. Leaving the field out entirely lets the provider use its normal limit.
- The `httpx.post(...)` call and `raise_for_status()` are unchanged, except that the body is
  now `json=payload`.
- `body: dict[str, Any] = response.json()` parses the reply and tells mypy it is a
  dictionary.
- `METER.record(body.get("usage") or {})` adds this response's token counts to the meter.
  `body.get("usage") or {}` rather than `body.get("usage", {})`: some responses carry
  `"usage": null`, and the `or` handles both the missing key and the null.
- `return body` hands back the whole response, so callers that need more than the text can
  have it.

*The new `ask(messages)`.* Same signature as yesterday, so `turn` does not change. It calls
`post` and pulls out the text exactly as before.

*`prompt_tokens(text)`.* Asks the server how many tokens a piece of text is. It sends the
text as a single user message with `max_tokens=1`, so the model writes at most one token
and the request costs almost nothing, then returns `usage.prompt_tokens`, the server's own
count of the input. This is the `count` function `chars_per_token` is given.

Then add one line at the end of `main`, after the transcript is written (after the line that
prints the message count):

**Add this code:**

    print(f"[meter] {METER}", file=sys.stderr)

That prints the meter's summary to the error stream at the end of every agent run.

Yesterday's `turn` is untouched.

**Check it:**

    uv run mypy src

`Success: no issues found`. Then `uv run python -c "import cartographer.agent"` must run
silently. An `ImportError` mentioning a "partially initialized module" means the
`agent` import in `budget.py`'s `main` was moved to the top of the file.

## Step 4 — Write `tests/test_budget.py`

**Where:** `tests/test_budget.py` — new file.
**Why this file exists:** all three run offline. They pin the maths, the skip list and the
pricing, which are the three parts that can be wrong without anything crashing.

**Add this code:**

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

**What each part does:**

*The calibration test.* `counter` is a fake token counter with a known answer: a fixed
overhead of 11 tokens plus one token per 4 characters (`//` is whole-number division). Fed
a 40-character and a 4,000-character string, it reports 21 and 1,011 tokens. The
subtraction gives 3,960 characters over 990 tokens, exactly `4.0`.

The first test is the important one. A counter with a fixed overhead of 11 tokens and a
true ratio of 4 must yield exactly 4.0 — that is the whole claim of the two-point method,
asserted rather than described. A one-sample version would report 40 / 21, about 1.9.

*The skip-list test.* `tmp_path` is a pytest fixture: a fresh empty folder for this test,
deleted afterwards. The test builds a tiny fake repository: one real file under `src/` and
one under `.venv/`. `measure` must count only the first, and `"x = 1\n"` is 6 characters
(the line break counts as one).

*The pricing test.* At $1 per million input tokens and $10 per million output tokens, a
million input tokens cost $1 and a hundred thousand output tokens cost $1, so `2.0`. If the
two directions were added together and priced at one rate, the answer would be wrong.

**Check it:**

    uv run pytest -q

`5 passed`: these three, the version test and the transcript test.

## Step 5 — Calibrate, then measure

**Where:** the repo root, with `OPENROUTER_API_KEY` set in this terminal.
**Why this step exists:** first against the project itself, which is small enough that a
wrong answer is obvious.

**Run this:**

    uv run python -m cartographer.budget .

**What each part does:** runs `budget.main` with `.` (the current folder) as the repository.

**Check it:** two requests go out, each capped at one output token. Note the ratio it
prints; if you change `CARTOGRAPHER_MODEL`, it changes, which is exactly why it is measured
and not hardcoded. Expect a few characters per token for code; the exact
value depends on the model's tokenizer, which is why you measure it. A `ZeroDivisionError` means the model returned the same count for both samples;
switch model.

The `calibration` line should read `2 calls`, with a small input count and an output of at
most 2. It prints `budget.METER` rather than the plain `METER` for a reason worth knowing:
`python -m cartographer.budget` loads `budget.py` under the name `__main__`, and when
`agent.py` then imports `cartographer.budget` it gets a second, separate copy of the module
with its own `METER`. The two calls are recorded on that copy, the one `agent.py` uses, and
`from cartographer import budget` inside `main` reaches exactly that copy. Print the plain
`METER` instead and the line reads `0 calls` even though two requests went out.

Then measure the target, the repository you did not write. Day 00 cloned it once, pinned
to click 8.5.0, so there is nothing to clone today; the same copy serves the whole series,
which is what keeps numbers from different days comparable.

    git -C "$CARTOGRAPHER_TARGET" rev-parse HEAD
    uv run python -m cartographer.budget "$CARTOGRAPHER_TARGET"

- `git -C "$CARTOGRAPHER_TARGET" rev-parse HEAD` prints the full commit id, the **SHA**, of
  the target: `8b19813f2bfca99f1018a587a8cf54fc959f2e5d`. `-C` runs git as if you were in
  that folder. Copy it; it goes in the table in Step 6.
- The second line measures the target. The double quotes keep the path in one piece even if
  it contains a space.

The `.` run at the start of this step is the other row: cartographer itself, whose SHA
`git rev-parse HEAD` at the repo root prints. That makes two rows.

**Record the commit SHA with every number.** A measurement against a moving branch is not
a measurement.

## Step 6 — Create `docs/measurements.md`

**Where:** `docs/measurements.md` — new file (create the `docs/` folder with
`mkdir -p docs`).
**Why this file exists:** create it and fill in a row per repository. This file, not the
blog post, is where the numbers live, because they change with every commit of the target.

**Add this code:**

    # Measurements

    Model: <the value of CARTOGRAPHER_MODEL>
    Ratio: <characters per token, from the two-point calibration>
    Date: <today>

    | repo | commit | files | characters | estimated tokens |
    |---|---|---|---|---|
    |  |  |  |  |  |

**What each part does:** the three header lines record what the numbers depend on: the
model (the ratio is per model), the ratio itself, and the date. The table has one row per
repository; replace the empty row with real ones, copying `files`, `characters` and
`tokens` from the output of Step 5 and the SHA from `rev-parse`.

**Check it:** at least two filled rows, each with a 40-character commit SHA.

## Step 7 — Lint, types, tests, commit and tag

**Where:** the repo root.
**Why this step exists:** run the same checks CI runs, then get the day onto `main`.

**Run this:**

    uv run ruff check . && uv run ruff format .
    uv run mypy src
    uv run pytest -q

Lint and format, type-check, test. All three must be clean before you commit.

    git add -A
    git commit -m "Day-03 | <your name> | Add. Token measurement and per-call metering"

Then bring the day onto your local `main` and tag it:

    git checkout main
    git merge day-03-token-budget
    git tag day-03

**What each part does:**

- `git add -A` stages every new and changed file; anything `.gitignore` lists is skipped.
- `git commit -m "..."` records them as one commit, in the series' commit format from Day 00, Step 12; `Add` because both are new.
- `git checkout main` switches back to the main branch.
- `git merge day-03-token-budget` brings today's commit onto `main`. Because `main` has not moved since
  you branched, git simply moves `main` forward to your commit (a **fast-forward**), with no
  extra merge commit. If `main` already contains the branch, it prints `Already up to date.`
  and changes nothing.
- `git tag day-03` puts a local bookmark on the finished day, so `git diff day-02 day-03`
  shows exactly what today changed.

**Check it:** `git log --oneline -3` shows today's commit at the top, on `main`, with
`tag: day-03` beside it.

## Check before you call it done

- `python -m cartographer.budget .` prints a ratio, a token estimate and a `calibration 2 calls` meter line
- Running the agent on two files prints a `[meter]` line with a non-zero input count
- `docs/measurements.md` has at least two repositories in it, each with a commit SHA
- No price literal anywhere in `src/`
- You can state the estimated token count of one real repository and say whether it fits
