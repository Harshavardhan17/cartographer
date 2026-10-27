# Day 04: Stop parsing prose. Make the model return a struct

Dev notes for this day's post: [read the post](https://harshakatkam.dev/stop-parsing-prose).
Step numbers follow the full build guide; steps only the repository owner needs, such as publishing to GitHub, are left out. New here? Start with [how to use these notes](README.md).

---

**Today's build:** stop parsing prose

Today the agent stops returning paragraphs and starts returning records: a `Symbol` and a
`Finding` you can count, diff and assert on. With the schema on the wire, a hand-written
validator behind it, and a repair loop for when the model ignores both.

Three terms you will meet today. A **JSON Schema** is a machine-readable description of
the shape some JSON must have: which keys, what types, which values are allowed.
**Structured output** is a request feature where you send such a schema and a provider that
supports it constrains **decoding** (the token-by-token generation of the reply) so the
reply fits it. A **validator** is your own code that checks the reply really does fit,
because the request is only a request.

Time: about 90 minutes.

## Where you are starting from

`~/workspace/personal/cartographer` on `main`, from yesterday:

- `src/cartographer/agent.py` — `post(messages, max_tokens=None)` which records `usage`
  into the meter, `ask(messages)`, `prompt_tokens(text)`, `turn(messages, content)`, and a
  `main` that walks the files you name and dumps `transcript.json`.
- `src/cartographer/budget.py` — `source_files`, `measure`, `chars_per_token`, `Meter`,
  `METER`, and a `main` that sizes a repository.
- `tests/test_package.py`, `tests/test_agent.py`, `tests/test_budget.py` — all offline.
- `docs/measurements.md` with a row per pinned test repository.
- `.gitignore` already contains `maps/` and `transcript.json`.

Everything the agent produces is still prose. You cannot diff two runs, you cannot count
what it found, and a test can only assert that a string is non-empty.

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
| `src/cartographer/records.py` | New | The typed records (`Symbol`, `Finding`, `FileReport`), the JSON Schema sent with each request, the instruction that explains it, and the validator that turns a reply into records or a precise error |
| `src/cartographer/agent.py` | Edited | Sends the schema, adds `describe_file` with a repair loop, and replaces `main` so it prints records and writes `maps/records.json` |
| `tests/test_records.py` | New | Seven offline tests of the validator: valid input, fenced input, and each way a reply can be malformed |
| `tests/test_agent.py` | Edited (replaced) | Two offline tests of the repair loop |

## Commands and tools today

| Command | What it does |
|---|---|
| `echo "$CARTOGRAPHER_TARGET"` | Readiness check, part one: prints the target's path |
| `git -C "$CARTOGRAPHER_TARGET" rev-parse HEAD` | Readiness check, part two: prints the target's commit |
| `cd ~/workspace/personal/cartographer` | Moves to the repo root |
| `git checkout main` | Switches to the main branch |
| `git checkout -b day-04-structured-records` | Creates today's branch and switches to it |
| `git branch --show-current` | Prints the branch you are on |
| `uv run python -c "from cartographer.records import Symbol; ..."` | Builds one `Symbol` and prints it, proving the record types import |
| `uv run python -c "from cartographer.records import REPORT_SCHEMA; ..."` | Prints the start of the JSON Schema |
| `uv run python -c "from cartographer.records import REPAIR; ..."` | Prints the repair prompt with a sample error filled in |
| `uv run python -c "from cartographer.records import require; ..."` | Runs the type check on one field, once passing and once failing |
| `uv run python -c "from cartographer.records import parse_report; ..."` | Parses a minimal valid reply into a `FileReport` |
| `uv run ruff check src` | Lints the package, to catch a duplicated or unused import |
| `uv run mypy src` | Type-checks the package |
| `uv run pytest tests/test_records.py -q` | Runs only the new validator tests |
| `uv run pytest -q` | Runs every test |
| `uv run python -m cartographer.agent src/cartographer/budget.py` | Asks the real model for records about one file |
| `cat maps/records.json` | Prints the saved records |
| `git status --short` | Confirms `maps/` is ignored |
| `CARTOGRAPHER_STRUCTURED=0 uv run python -m cartographer.agent src/cartographer/budget.py` | The same with the schema switched off, to exercise the repair loop |
| `uv run ruff check . && uv run ruff format .` | Lints, then formats every file |
| `git add -A` | Stages every new and changed file |
| `git commit -m "..."` | Records today's work as one commit |
| `git checkout main` | Switches back to the main branch |
| `git merge day-04-structured-records` | Brings today's branch onto `main` |
| `git tag day-04` | Bookmarks the finished day |
| `git log --oneline -3` | Shows the last three commits |

New tools today: none

## Step 1 — Start a branch for today

**Where:** the repo root, `~/workspace/personal/cartographer`.
**Why this step exists:** one branch per day, merged the same day.

**Run this:**

    cd ~/workspace/personal/cartographer
    git checkout main
    git checkout -b day-04-structured-records

**What each part does:** `cd` moves to the repo root; `git checkout main` switches to the
main branch, which holds every finished day; `git checkout -b day-04-structured-records` creates today's
branch from it and switches to it (`-b` is "create, then switch").

**Check it:** `git branch --show-current` prints `day-04-structured-records`.

## Step 2 — Start `src/cartographer/records.py` with the record types

**Where:** `src/cartographer/records.py` — new file.
**Why this file exists:** new module, and the most important one so far. It owns three
things that have to change together: the Python types, the JSON Schema sent on the wire,
and the words that explain that schema to the model. Splitting them across files is how
they drift. Steps 2 to 6 build it up in order; each one adds to the bottom of the file.

**Add this code:**

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

**What each part does:**

*Imports.* `json` parses the model's reply. `os` reads one environment variable. `dataclass`
generates record classes. From `typing`: `Any` means "any type", `TypeVar` declares a type
placeholder. Both are used further down the file.

*`KINDS` and `CONFIDENCES`.* The only values allowed in a symbol's `kind` and a finding's
`confidence`. They are **tuples** (round brackets): fixed, ordered lists that cannot be
changed by accident. One definition feeds both the schema and the validator, so the two
can never disagree.

*`T = TypeVar("T")`.* A placeholder type. It lets `require` (Step 5) say "whatever type you
ask me to check for is the type I return", so asking for `str` gives mypy a `str`.

*`InvalidReport`.* The one exception the validator raises. Subclassing `ValueError` (the
standard "right type, wrong value" error) means generic handlers still catch it, while
`except InvalidReport` catches only validation failures. `pass` means the class adds
nothing beyond its name.

*`Symbol`.* One definition in a file that a newcomer needs to know about: its `name`, its
`kind` (one of `KINDS`), the `file` it lives in, the `line` it starts on, and its `role`, a
sentence on why it matters. `frozen=True` makes instances read-only after creation, which
also lets two symbols be compared with `==` safely in tests.

*`Finding`.* One conclusion about a file: the `claim`, the `evidence` it rests on (a quoted
or named line) and a `confidence` of `high` or `low`.

*`FileReport`.* Everything the model says about one file: a list of symbols and a list of
findings. Not frozen, because it holds lists.

**Check it:**

    uv run python -c "from cartographer.records import Symbol; print(Symbol('m', 'function', 'a.py', 1, 'r'))"

It prints `Symbol(name='m', kind='function', file='a.py', line=1, role='r')`.

## Step 3 — Add the schema and the request field to `records.py`

**Where:** `src/cartographer/records.py` — edit to the file from Step 2. Add this at the
bottom.
**Why this change exists:** this is the JSON Schema that travels with the request, and the
`response_format` field that carries it. One helper, because the two rules that make a
strict schema work — every property required, no extra properties — must hold at every
level, and writing them out four times is how you forget one.

**Add this code:**

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

**What each part does:**

*`json_object(properties)`.* Builds the schema for one JSON object from a dictionary of its
fields. `"type": "object"` says it is a JSON object. `"properties"` describes each field.
`"required": list(properties)` makes every field mandatory (`list()` of a dictionary gives
its keys). `"additionalProperties": False` forbids any field not listed. Python's `False`
becomes JSON's `false` when sent.

*`SYMBOL_SCHEMA`.* The shape of one symbol, field for field matching the `Symbol` class.
`"enum": list(KINDS)` restricts `kind` to the five allowed values; `"integer"` is JSON
Schema's word for a whole number.

*`FINDING_SCHEMA`.* The shape of one finding, with `confidence` restricted to
`CONFIDENCES`.

*`REPORT_SCHEMA`.* The whole reply: an object with two arrays. `"items"` gives the schema
every element of the array must match, so the symbol and finding rules apply inside.

*`STRUCTURED`.* A switch. It is `True` unless the environment variable
`CARTOGRAPHER_STRUCTURED` is set to `"0"`. It exists so you can turn the schema off and see
what the validator alone achieves.

*`RESPONSE_FORMAT`.* The value sent as the request's `response_format` field, or `None`
when the switch is off. The `X if condition else Y` form picks one of two values.
`"type": "json_schema"` says a schema follows, `"name"` labels it, `"strict": True` asks for
strict enforcement, and `"schema"` is the schema itself.

`response_format` is the OpenAI-compatible field OpenRouter forwards. `strict: true` asks
the provider to constrain decoding to the schema rather than merely suggest it. Not every
model behind the free tier supports it, and when the provider does not, you get either an
error or plain prose back — which is exactly why `CARTOGRAPHER_STRUCTURED=0` exists and why
the validator below is not optional. Re-check the field names against
`https://openrouter.ai/docs/features/structured-outputs` before you change anything here;
this is the one part of the file that can rot without anyone editing it.

**Check it:**

    uv run python -c "from cartographer.records import REPORT_SCHEMA; import json; print(json.dumps(REPORT_SCHEMA)[:120])"

It prints the start of the schema as JSON, beginning `{"type": "object", "properties":`.

## Step 4 — Add the instruction and the repair prompt to `records.py`

**Where:** `src/cartographer/records.py` — edit; add at the bottom.
**Why this change exists:** now the words. The schema constrains shape; only prose can carry
meaning.

**Add this code:**

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

**What each part does:**

*`INSTRUCTION`.* Sent in front of every file. The first line states the output format. The
`"symbols"` paragraph names every field and says what each means, which the schema cannot:
that `file` must be the path exactly as given, and `role` is one sentence. The `"findings"`
paragraph defines the confidence rule in terms the model can apply: `high` only when the
file shows it. The last line forbids reporting anything the file does not show and says
empty lists are acceptable, so the model is never pushed to invent symbols to fill the
shape.

*`REPAIR`.* Sent back when a reply fails validation. `{error}` is a placeholder filled with
the validator's message, so the model is told exactly what was wrong. The second line rules
out the three things models most often wrap around JSON: an explanation, a Markdown code
fence, and a preamble.

**Check it:** `uv run python -c "from cartographer.records import REPAIR; print(REPAIR.format(error='x'))"`
prints the repair prompt with `x` in place of the error.

## Step 5 — Add the validator's building blocks to `records.py`

**Where:** `src/cartographer/records.py` — edit; add at the bottom.
**Why this change exists:** and the validator. This is the part a tutorial skips.

**Add this code:**

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

**What each part does:**

*`FENCE`.* Three backticks, the Markdown marker that opens and closes a code block. Models
often wrap JSON in one even when told not to.

*`strip_fences(text)`.* Removes such a wrapper if there is one.

- `text.strip()` drops leading and trailing whitespace.
- If the text does not start with a fence, it is returned as is.
- `stripped[len(FENCE) :]` slices off the opening three backticks.
- If what follows is the language tag `json`, that is sliced off too.
- `body.rsplit(FENCE, 1)[0]` splits once at the last fence and keeps everything before it,
  discarding the closing fence and anything after it. `.strip()` tidies the result.

*`require(payload, key, expected)`.* Fetches one field and checks its type.

- `expected: type[T]` means "a type, such as `str` or `int`", and the return type `T` is
  that same type.
- A missing key raises `missing required field 'line'`. `{key!r}` inserts the key with
  quotes, so the message is unambiguous.
- `value: object = payload[key]` reads the field into a variable declared as `object`, the
  type every Python value has. That annotation matters for mypy: a value of type `Any` would
  switch type checking off for it, while an `object` has to be proven to be something more
  specific before it can be returned as one.
- `isinstance(value, expected)` checks the type. The extra `isinstance(value, bool)` guard
  is there because `True` is an `int` in Python, so a model that answers `"line": true`
  would otherwise sail through a `line: int` check. (None of the fields is a boolean, so
  rejecting every boolean is safe.)
- The error names the field, what was expected and what arrived, using each type's
  `__name__` (`int`, `str`).
- `return value` hands the field back. mypy accepts it as a `T` because the `isinstance`
  check above has proven it: past the `raise`, the only values left are instances of
  `expected`. No cast is needed, and recent mypy versions report an unneeded cast as
  an error in strict mode.

*`one_of(value, allowed, field)`.* Checks that a string is one of the allowed values, and
if not, names the field, the bad value and the full allowed list (`', '.join(...)` turns
the tuple into `high, low`). `tuple[str, ...]` means a tuple of strings of any length.

**Check it:** `uv run python -c "from cartographer.records import require; print(require({'line': 3}, 'line', int))"`
prints `3`. Change the `3` to `True` and it raises `InvalidReport: field 'line' must be int, got bool`.

## Step 6 — Add the record builders and `parse_report` to `records.py`

**Where:** `src/cartographer/records.py` — edit; add at the bottom. This completes the file.
**Why this change exists:** these turn a reply into typed records, or raise an error the
model can act on.

**Add this code:**

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

**What each part does:**

*`to_symbol(item)`.* Takes one element of the `symbols` array. If it is not a dictionary
(a JSON object), it raises. Otherwise it builds a `Symbol`, fetching each field with
`require`, and checking `kind` against `KINDS` with `one_of`. The first problem found
raises; nothing half-built is returned.

*`to_finding(item)`.* The same for one finding, with `confidence` checked against
`CONFIDENCES`.

*`load_object(text)`.* Strips any fence, then `json.loads` parses the text. If it is not
valid JSON, the `JSONDecodeError` is converted into `InvalidReport("not JSON: ...")`, keeping
the parser's message, which says where the JSON broke. `from error` chains the original
exception so a traceback still shows it. Valid JSON that is not an object (a bare list,
say) is rejected too.

*`parse_report(text)`.* The entry point. Load the object, require both arrays to be lists,
and build every symbol and finding through the functions above. Each square-bracket
expression is a **list comprehension**: a compact loop that builds a list.

Every `InvalidReport` message is written to be read by the model, not by you. `missing
required field 'line'` is a repair instruction; `KeyError` is not. That is the whole
design of the error path.

No `jsonschema` dependency. The runtime dependency list stays at `httpx`, and a validator
you wrote is a validator whose error messages you control.

**Check it:**

    uv run python -c "from cartographer.records import parse_report; print(parse_report('{\"symbols\": [], \"findings\": []}'))"

It prints `FileReport(symbols=[], findings=[])`.

## Step 7 — Update the imports in `agent.py`

**Where:** `src/cartographer/agent.py` — edit to an existing file; the import lines at the
top.
**Why this change exists:** the agent now needs the records module, plus `asdict` to save
records as JSON.

Every existing import stays: `json`, `os`, `pathlib`, `sys`, `from typing import Any`,
`httpx` and the `METER` import. Add two more. Put `from dataclasses import asdict` with the
standard-library imports, after `import sys`; put the `cartographer.records` import on the
line after the `METER` import.

**Add this code:**

    from dataclasses import asdict

    from cartographer.records import (
        INSTRUCTION,
        REPAIR,
        RESPONSE_FORMAT,
        FileReport,
        InvalidReport,
        parse_report,
    )

Do not add a second `import json` or `from typing import Any`: both are already in the file
(since the transcript day and yesterday), and each import must appear once.

**What each part does:**

- `asdict` converts a dataclass, nested ones included, into plain dictionaries and lists
  that `json.dumps` can handle.
- `json`, already imported, is still needed: `main` will write the records as JSON. `Any`,
  also already there, is used in the new type hints of `post`, `ask` and `turn`.
- From `records`: the instruction and repair prompts, the response format, the
  `FileReport` type, the exception, and the parser. The round brackets let one import span
  several lines.

**Check it:** `uv run ruff check src` should not report `F811` (redefinition) or `F401`
(unused import) for these lines once Steps 8 to 11 are done.

## Step 8 — Replace the transcript path with a maps folder

**Where:** `src/cartographer/agent.py` — edit; find the line `TRANSCRIPT = pathlib.Path("transcript.json")`.
**Why this change exists:** the output is now records, written into the `maps/` folder.

Replace the `TRANSCRIPT` constant with this line.

**Add this code:**

    MAPS = pathlib.Path("maps")

**What each part does:** `MAPS` is the folder the agent writes its output to, relative to the
repo root. `maps/` has been in `.gitignore` since the first commit.

The transcript file goes today. It was a debugging artefact for prose, and `maps/records.json`
supersedes it. Leave the `transcript.json` line in `.gitignore` — the file comes back when
the agent starts a multi-turn tool exchange worth debugging.

Two lines above it, change the default model. OpenRouter withdrew the free
`nvidia/nemotron-3-super-120b-a12b:free`, so the line becomes:

    MODEL = os.environ.get("CARTOGRAPHER_MODEL", "nvidia/nemotron-3.5-super-vl:free")

Its free successor accepts the same requests, including today's `response_format`.

## Step 9 — Update the system message

**Where:** `src/cartographer/agent.py` — edit; find `SYSTEM = """...` and replace the whole
string.
**Why this change exists:** the persona has to match the new output, and one instruction
from the memory day no longer applies.

**Add this code:**

    SYSTEM = """You are mapping a repository you have never seen, one file at a time.

    Where the file you have been shown does not answer a question, record that as a
    finding with low confidence rather than guessing.
    """

**What each part does:** the first sentence is unchanged. The sentence asking the model to
"refer back to files you have already been shown" is gone: from today each file is
described in its own fresh conversation (Step 10), so there are never earlier files to
refer back to, and an instruction the model cannot follow only invites it to invent some.
The last sentence now tells the model what to do with a gap in its knowledge in terms of
the new records: write a low-confidence finding instead of a guess.

## Step 10 — Thread `response_format` through, and add `describe_file`

**Where:** `src/cartographer/agent.py` — edit. Find the functions `post`, `ask` and `turn`
and replace all three with the versions below; then add `describe_file` straight after
`turn`. `prompt_tokens` stays where it is, between `ask` and `turn`, unchanged.
**Why this change exists:** thread `response_format` through `post`, `ask` and `turn`, then
add `describe_file`, which asks about one file and repairs bad replies.

**Add this code:**

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

**What each part does:**

*`post`.* Yesterday's version with one new optional parameter, `response_format`. The
signature is split over several lines only because it got long. The new
`if response_format is not None: payload["response_format"] = response_format` adds the
field only when there is one, so when the schema is switched off nothing is sent. Everything
else is unchanged.

*`ask`.* Gains the same optional parameter and passes it to `post` by name. It still
returns the reply's text.

*`turn`.* Gains the same optional parameter and passes it on to `ask`. Both appends are
unchanged: user message in, assistant reply in.

`prompt_tokens` is untouched and still works, because `post` kept its old parameters.

*`describe_file(path, attempts=3)`.* Ask about one file until the reply validates, at most
`attempts` times.

- `messages` starts a fresh transcript with only the system message: each file is its own
  conversation.
- `content` is the instruction, a label line, and the file's text.
- `for attempt in range(1, attempts + 1)` counts 1, 2, 3, so the numbers in the log read
  naturally.
- `reply = turn(messages, content, RESPONSE_FORMAT)` sends the current content with the
  schema and records both sides.
- `return parse_report(reply)` returns the records if the reply is valid, ending the loop.
- `except InvalidReport as error` catches a bad reply. The `print` logs which attempt failed
  and why, on stderr.
- `if attempt == attempts: raise` gives up on the last attempt and re-raises the same error.
- Otherwise `content` becomes the repair prompt with the error filled in, and the loop sends
  it as the next user message.
- The final `raise` after the loop runs only if the loop never ran at all.

The repair loop reuses `turn`, so the rejected answer stays in the transcript. That matters:
the model has to see its own bad output next to the complaint about it, or the correction
has nothing to attach to. The trailing `raise` is not dead code — it is the path taken when
somebody passes `attempts=0`.

**Check it:** `uv run mypy src` reports exactly one error: the old `main` still uses
`TRANSCRIPT`, which no longer exists. Step 11 replaces `main` and clears it.

## Step 11 — Replace `main`

**Where:** `src/cartographer/agent.py` — edit; find the function `main` and replace it, and
the `if __name__` guard below it, with this.
**Why this change exists:** the command now prints records and saves them, instead of
printing paragraphs and a transcript.

**Add this code:**

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

**What each part does:**

- The first three lines are unchanged: turn the command-line words into paths, or print
  usage.
- `MAPS.mkdir(exist_ok=True)` creates `maps/` if it does not exist; `exist_ok=True` means no
  error if it does.
- `reports` maps each file's path (as a string) to its `FileReport`.
- For each path: `describe_file` gets the records, they are stored, and a header line is
  printed.
- Each symbol prints as one aligned row. Inside an f-string, `:11` pads to 11 characters,
  `:24` to 24, and `:<6` left-aligns in 6, so the columns line up.
- Each finding prints with its confidence in brackets, padded to 4 characters so `high`
  and `low ` align.
- After the loop, `json.dumps({...}, indent=2)` turns every report into JSON. The braces are
  a **dictionary comprehension**: a compact loop that builds a dictionary, here from path
  to `asdict(report)`. `MAPS.joinpath("records.json")` is the path `maps/records.json`.
- The meter line is printed last, as yesterday.

**Check it:** `uv run mypy src` reports `Success: no issues found`.

## Step 12 — Write `tests/test_records.py`

**Where:** `tests/test_records.py` — new file.
**Why this file exists:** all offline, all real assertions. Every one of these is a failure a
model has actually produced.

**Add this code:**

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

**What each part does:**

*`VALID`.* A correct reply as a Python dictionary: one symbol and one finding. Every test
starts from it, so each test changes exactly one thing.

*The happy path.* `json.dumps(VALID)` turns it into the text a model would send;
`parse_report` must return a `Symbol` equal, field for field, to the expected one. `==`
works because dataclasses compare by their fields.

*The fence.* Wraps the same JSON in a Markdown code fence tagged `json`, the most common
wrapper, and checks it still parses.

*The missing field.* `json.loads(json.dumps(VALID))` is a quick deep copy, so deleting from
`broken` cannot damage `VALID` for other tests. `del` removes `line`. `pytest.raises(...,
match="'line'")` passes only if `InvalidReport` is raised and its message contains `'line'`,
so it tests the message, not just the failure.

*The string line number.* `"46"` instead of `46`. The message must say exactly
`must be int, got str`.

*The bad enum.* `"helper"` is not one of the five kinds.

*Prose.* A sentence instead of JSON must fail with `not JSON`.

*The schema itself.* Checks that extra keys are forbidden at the top level and in a symbol,
and that every symbol field is required. `set(...)` makes the comparison ignore order.

**Check it:** `uv run pytest tests/test_records.py -q` prints `7 passed`.

## Step 13 — Replace `tests/test_agent.py`

**Where:** `tests/test_agent.py` — edit; delete the old contents and replace them with this.
**Why this change exists:** the transcript test from the memory day still passes, but the
interesting contract today is the repair loop, and it is testable with no network at all.

**Add this code:**

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

**What each part does:**

*`GOOD` and `BAD`.* A valid empty report, and the kind of chatty prose a model sends
instead of JSON.

*The repair test.*

- `replies = [BAD, GOOD]` scripts the fake model: bad first, good second.
- `sent` records what each call was given. `[dict(message) for message in messages]` copies
  every message at that moment, because the real list keeps growing afterwards.
- `fake_ask` has the same parameters as the real `ask`; `replies.pop(0)` returns and removes
  the first scripted reply.
- `monkeypatch.setattr(agent, "ask", fake_ask)` swaps it in. `turn` looks up `ask` at call
  time, so `describe_file` uses the fake.
- `tmp_path / "sample.py"` writes a real one-line file for `describe_file` to read.
- The assertions: the final result is the empty report from `GOOD`; exactly two calls were
  made; in the second call, the second-to-last message (`[-2]`) is the rejected `BAD` reply,
  and the last (`[-1]`) is the repair prompt containing the `not JSON` error.

*The give-up test.* `always_bad` always returns prose and counts calls; `nonlocal calls`
lets the inner function change the outer variable. With `attempts=2`, `describe_file` must
raise `InvalidReport`, and must have asked exactly twice, not three times and not forever.

The two assertions on `sent[1]` are the ones that earn their place: the rejected answer is
in the transcript at `[-2]`, and the complaint the model has to act on is at `[-1]`. Get
that order wrong and the repair loop silently degrades into three identical attempts.

**Check it:** run them:

    uv run pytest -q

Expect `13 passed` — seven new in `test_records.py`, the two rewritten in `test_agent.py`,
plus the one in `test_package.py` and the three in `test_budget.py`. If your count differs,
read which file the extras are in; the number matters less than all of them passing.

## Step 14 — Confirm it works against the real endpoint

**Where:** the repo root, with `OPENROUTER_API_KEY` set.
**Why this step exists:** the tests prove the logic; this proves a real model's replies get
through it.

**Run this:**

    uv run python -m cartographer.agent src/cartographer/budget.py

**Check it:** expected shape of the output — the values will differ, the structure will not:

    --- src/cartographer/budget.py ---
      function    source_files             line 37     yields candidate source paths under a root
      function    measure                  line 46     counts files and total characters
      class       Meter                    line 56     accumulates token usage and prices it
      constant    METER                    line 83     the process-wide meter
      [high] the module makes no network call
      [low ] the skip list is aimed at Python projects specifically
    [meter] 1 calls  in 1187  out 291  $0.0000

The line numbers in that sample are illustrative. In the `budget.py` you wrote, the real
lines are 23 for `source_files`, 32 for `measure`, 42 for `Meter` (41 if the model counts
the `@dataclass` line) and 69 for `METER`;
comparing what the model reports against those is your first accuracy check.

Then confirm the two paths that are easy to get wrong:

    cat maps/records.json
    git status --short

The JSON should parse and contain `symbols` and `findings` arrays with the fields spelled
exactly as the dataclasses spell them. `git status` must not list `maps/` — it has been
ignored since the first commit.

Now force the failure path. Turn the schema off, so the model has only the instruction to
go on:

    CARTOGRAPHER_STRUCTURED=0 uv run python -m cartographer.agent src/cartographer/budget.py

`CARTOGRAPHER_STRUCTURED=0` before the command sets the switch for that one run, so
`RESPONSE_FORMAT` is `None` and no schema is sent.

Depending on the model you will either get the same clean output, or one or two
`[repair 1/3] ...` lines on stderr followed by clean output. Both are a pass. That second
case is the one worth watching, because it is what the schema is buying you, measured
rather than assumed.

## Step 15 — Lint, types, tests

**Where:** the repo root.
**Why this step exists:** run what CI runs.

**Run this:**

    uv run ruff check . && uv run ruff format .
    uv run mypy src
    uv run pytest -q

**What each part does:** lint and format, type-check strictly, run all thirteen tests.

**Check it:** all three clean. If ruff reports `F811` for `json` or `Any`, an import from
Step 7 was added a second time; delete the duplicate.

## Step 16 — Commit, merge and tag the day

**Where:** the repo root.
**Why this step exists:** the branch was created in Step 1, so you are already on it; this
gets the day onto `main`.

**Run this:**

    git add -A
    git commit -m "Day-04 | <your name> | Update. Typed symbol and finding records instead of prose"

Then bring the day onto your local `main` and tag it:

    git checkout main
    git merge day-04-structured-records
    git tag day-04

**What each part does:**

- `git add -A` stages every new and changed file; anything `.gitignore` lists is skipped.
- `git commit -m "..."` records them as one commit, in the series' commit format from Day 00, Step 12; `Update` because the agent already answered; today changes what its answer looks like.
- `git checkout main` switches back to the main branch.
- `git merge day-04-structured-records` brings today's commit onto `main`. Because `main` has not moved since
  you branched, git simply moves `main` forward to your commit (a **fast-forward**), with no
  extra merge commit. If `main` already contains the branch, it prints `Already up to date.`
  and changes nothing.
- `git tag day-04` puts a local bookmark on the finished day, so `git diff day-03 day-04`
  shows exactly what today changed.

**Check it:** `git log --oneline -3` shows today's commit at the top, on `main`, with
`tag: day-04` beside it.

## Before you call it done

- `uv run python -m cartographer.agent src/cartographer/budget.py` prints records, not paragraphs
- `maps/records.json` parses, and `git status --short` does not mention it
- `uv run pytest -q` is green, and at least one test asserts on the *content* of the repair message
- `CARTOGRAPHER_STRUCTURED=0` still produces a valid report, via the repair loop if needed
- `uv run mypy src` clean — the `isinstance` check in `require` is what keeps it that way
- No `jsonschema` in `pyproject.toml`; the dependency list is still just `httpx`
- You can say out loud why the schema is a request and the validator is the guarantee
