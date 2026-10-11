# Day 02: An LLM is a stateless function. Everything else is you

Dev notes for this day's post: [read the post](https://harshakatkam.dev/llm-is-a-stateless-function).
Step numbers follow the full build guide; steps only the repository owner needs, such as publishing to GitHub, are left out. New here? Start with [how to use these notes](README.md).

---

**Today's build:** memory by hand

Starting point: yesterday's `src/cartographer/agent.py`. Forty lines, one hardcoded
`TARGET`, `ask(prompt: str) -> str` building a one-message request. It works and it can
only ever look at one file.

Today it looks at several, and remembers the earlier ones. Nothing new gets installed —
the change is that `ask` takes the whole `messages` list instead of a single string, and
the caller owns that list.

Time: about 45 minutes.

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
| `src/cartographer/agent.py` | Edited (rewritten) | Now reads any files named on the command line and keeps one growing transcript of the conversation |
| `.gitignore` | Edited | Adds `transcript.json`, the debugging dump of that conversation |
| `tests/test_agent.py` | Edited (replaced) | Tests that each turn records both your message and the model's reply |

## Commands and tools today

| Command | What it does |
|---|---|
| `echo "$CARTOGRAPHER_TARGET"` | Readiness check, part one: prints the target's path |
| `git -C "$CARTOGRAPHER_TARGET" rev-parse HEAD` | Readiness check, part two: prints the target's commit |
| `cd ~/workspace/personal/cartographer` | Moves to the repo root |
| `git checkout main` | Switches to the main branch |
| `git checkout -b day-02-transcript` | Creates today's branch and switches to it |
| `git branch --show-current` | Prints the branch you are on |
| `uv run python -m cartographer.agent` | With no files named, prints the usage line and makes no request |
| `uv run pytest -q` | Runs the tests |
| `uv run python -m cartographer.agent pyproject.toml src/cartographer/agent.py` | Sends two related files, one turn each, then asks which to read first |
| `cat transcript.json` | Prints the saved conversation: the agent's entire state |
| `git status --short` | Confirms `transcript.json` is ignored |
| `uv run python -m cartographer.agent pyproject.toml src/cartographer/agent.py tests/test_agent.py` | The same with three files, to watch the transcript grow |
| `uv run ruff check . && uv run ruff format .` | Lints, then formats every file |
| `uv run mypy src` | Type-checks the package |
| `git add -A` | Stages every new and changed file |
| `git commit -m "..."` | Records today's work as one commit |
| `git checkout main` | Switches back to the main branch |
| `git merge day-02-transcript` | Brings today's branch onto `main` |
| `git tag day-02` | Bookmarks the finished day |
| `git log --oneline -3` | Shows the last three commits |

New tools today: none

The key from yesterday lives only in the terminal you loaded it in. In a new terminal, load
it again with yesterday's `read -rs` line before any step that calls the model.

## Step 1 — Start a branch for today

**Where:** the repo root, `~/workspace/personal/cartographer`.
**Why this step exists:** one branch per day, merged the same day.

**Run this:**

    cd ~/workspace/personal/cartographer
    git checkout main
    git checkout -b day-02-transcript

**What each part does:** `cd` moves to the repo root; `git checkout main` switches to the
main branch, which holds every finished day; `git checkout -b day-02-transcript` creates today's
branch from it and switches to it (`-b` is "create, then switch").

**Check it:** `git branch --show-current` prints `day-02-transcript`.

## Step 2 — Rewrite `src/cartographer/agent.py`

**Where:** `src/cartographer/agent.py` — edit to an existing file. The changes touch almost
every part, so replace the whole file with the version below.
**Why this change exists:** a model remembers nothing between requests. To make it
"remember" an earlier file, your code has to send that file again, inside a list of every
message so far. That list is the **transcript**.

Three changes: `TARGET` and `PROMPT` go, `SYSTEM` and `TRANSCRIPT` arrive, and `ask`
changes signature. `OPENROUTER_URL`, `MODEL` and the body of `ask` are the same as
yesterday.

**Add this code:**

    import json
    import os
    import pathlib
    import sys

    import httpx

    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    MODEL = os.environ.get("CARTOGRAPHER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")
    TRANSCRIPT = pathlib.Path("transcript.json")

    SYSTEM = """You are mapping a repository you have never seen, one file at a time.

    Refer back to files you have already been shown, by name. Where the files you
    have seen do not answer a question, answer that you cannot tell.
    """

    def ask(messages: list[dict[str, str]]) -> str:
        response = httpx.post(
            OPENROUTER_URL,
            headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
            json={"model": MODEL, "messages": messages},
            timeout=120.0,
        )
        response.raise_for_status()
        body = response.json()
        return str(body["choices"][0]["message"]["content"])

    def turn(messages: list[dict[str, str]], content: str) -> str:
        messages.append({"role": "user", "content": content})
        reply = ask(messages)
        messages.append({"role": "assistant", "content": reply})
        return reply

    def main() -> None:
        paths = [pathlib.Path(argument) for argument in sys.argv[1:]]
        if not paths:
            sys.exit("usage: python -m cartographer.agent FILE [FILE ...]")

        messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM}]
        for path in paths:
            print(turn(messages, f"--- {path} ---\n{path.read_text()}"))
        print(turn(messages, "Which of these files would you read first, and why?"))

        TRANSCRIPT.write_text(json.dumps(messages, indent=2))
        print(f"\n{len(messages)} messages in {TRANSCRIPT}", file=sys.stderr)

    if __name__ == "__main__":
        main()

**What each part does:**

*Imports.* `import json` is new: it turns the transcript into text you can save. The rest
are unchanged from yesterday.

*Constants.* `OPENROUTER_URL` and `MODEL` are unchanged. `TRANSCRIPT` is new: the path of
the file the conversation is saved to after each run, relative to wherever you run the
command.

*`SYSTEM`.* This text becomes the **system message**: the standing instructions placed
first in the list, which the model treats as its brief for the whole conversation. It
replaces yesterday's `PROMPT`. Instead of a template with placeholders, it describes the
job ("one file at a time"), asks the model to refer back to earlier files by name (so you
can see whether memory is working), and keeps the permission to say "I cannot tell".

*`ask(messages)`.* The body is yesterday's, with one change: the parameter is now the whole
list of messages, typed `list[dict[str, str]]` (a list of dictionaries whose keys and
values are strings), and that list goes into the request as `"messages": messages` instead
of a one-item list built inside the function. `ask` no longer decides what the model sees;
its caller does.

*`turn(messages, content)`.* One exchange of the conversation, in four lines.

- `messages.append({"role": "user", "content": content})` adds your new message to the end
  of the list.
- `reply = ask(messages)` sends the whole list, every earlier message included. This is the
  only reason the model can "remember": it is reading the earlier turns again, right now.
- `messages.append({"role": "assistant", "content": reply})` adds the model's own answer to
  the list, with the role `assistant` (the model's side of the conversation).
- `return reply` hands the text back so the caller can print it.

Two things worth being deliberate about:

- `turn` mutates the list it is given rather than returning a new one. That is the
  point: there is exactly one transcript, the caller owns it, and every append is
  visible in one place.
- The assistant reply is appended as `{"role": "assistant", ...}` immediately. Skip that
  and the model never sees its own answers, which produces a subtler bug than no memory
  at all — see the post.

*`main()`.*

- `sys.argv[1:]` is the list of words typed after the command; `[0]` would be the program
  itself. The list comprehension turns each into a `pathlib.Path`.
- `if not paths: sys.exit("usage: ...")` stops with a usage line if you named no files. The
  `FILE [FILE ...]` notation means "one file, optionally more".
- `messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM}]` starts the
  transcript with the system message. The type annotation is there because mypy cannot
  infer the full type of a list from one literal.
- The `for` loop sends each file as one turn, labelled `--- path ---` and followed by its
  contents (`\n` is a line break), and prints each reply.
- The final `turn` asks a question that can only be answered well by remembering every file:
  which would you read first?
- `TRANSCRIPT.write_text(json.dumps(messages, indent=2))` saves the entire conversation as
  pretty-printed JSON (`indent=2` adds line breaks and two-space indentation so you can read
  it).
- The last `print` reports how many messages were sent. `file=sys.stderr` sends it to the
  error stream rather than normal output, so it stays separate from the model's answers if
  you redirect output to a file.

**Check it:**

    uv run python -m cartographer.agent

With no files named, it should print the usage line and exit without making a request.

## Step 3 — Ignore the transcript

**Where:** `.gitignore` — edit to an existing file. Add one line at the end, under `maps/`.
**Why this change exists:** the transcript contains whole source files and is regenerated
on every run. It is a debugging artefact, not source.

**Add this code:**

    transcript.json

**What each part does:** a line with no slashes or wildcards matches a file of exactly that
name anywhere in the repository, so git will never offer to commit it.

**Check it:** after Step 5 creates the file, `git status --short` must not list
`transcript.json`.

## Step 4 — Replace `tests/test_agent.py`

**Where:** `tests/test_agent.py` — edit to an existing file. Delete yesterday's contents
and replace them with the version below.
**Why this change exists:** yesterday's prompt test goes; `PROMPT` no longer exists. The
new one asserts the protocol, with no network.

**Add this code:**

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

**What each part does:**

- `import pytest` is needed for the `pytest.MonkeyPatch` type hint.
  `from cartographer import agent` imports the module itself, not names from it, so the test
  can replace something inside it.
- `monkeypatch` is a pytest **fixture**: a helper pytest creates and passes in because the
  test names it as a parameter. `monkeypatch.setattr(agent, "ask", ...)` replaces
  `agent.ask` for the duration of this one test, then puts the real one back.
- The replacement is a `lambda` (a one-line nameless function) that never touches the
  network and returns a string saying how many messages it was given. That makes the size
  of the list visible in the reply.
- `messages` starts with just the system message, exactly as `main` does.
- Two calls to `agent.turn` simulate two files.
- The first `assert` checks the order of roles: system, then user and assistant twice. If
  `turn` forgot to append the reply, the list would be `system, user, user`.
- `first == "saw 2 messages"` (system plus the first user message) and
  `second == "saw 4 messages"` (system, user, assistant, user) prove the second request
  carried the first exchange.

`monkeypatch.setattr` works here because `turn` looks `ask` up as a module global at call
time. The two return values are the real assertion: the second call saw four messages, so
the transcript genuinely grew.

**Check it:**

    uv run pytest -q

`2 passed`: this test and the version test.

## Step 5 — Run it on two related files

**Where:** the repo root.
**Why this step exists:** pick two files where the second obviously depends on the first,
so a memoryless answer is unmistakable.

**Run this:**

    uv run python -m cartographer.agent pyproject.toml src/cartographer/agent.py

**What each part does:** the two paths after the module name become `sys.argv[1:]`.
`pyproject.toml` declares `httpx`; `agent.py` imports it, so a model that remembers the
first file can connect the two.

**Check it:** read the final answer. If it names both files and explains the relationship,
the transcript is doing its job. Then open the artefact:

    cat transcript.json

That file is the entire state of the agent. There is nothing else. You should see one
`system` message, then `user` and `assistant` alternating, with the full text of both files
inside the `user` messages.

## Step 6 — Watch it grow

**Where:** the repo root.
**Why this step exists:** every turn re-sends everything before it, so the cost of a run
grows faster than the number of files.

Run it again with three files and compare.

**Run this:**

    uv run python -m cartographer.agent pyproject.toml src/cartographer/agent.py tests/test_agent.py

**Check it:** the message count on stderr goes from 7 to 9 (one system message, two per
file, two for the final question), and the last request carried every earlier file again.
Nothing measures that yet. Tomorrow it does.

## Step 7 — Lint, types, tests, commit and tag

**Where:** the repo root.
**Why this step exists:** run the same checks CI runs, then get the day onto `main`.

**Run this:**

    uv run ruff check . && uv run ruff format .
    uv run mypy src
    uv run pytest -q

Lint and format, type-check the package, run the tests. All three must be clean before you
commit.

    git add -A
    git commit -m "Day-02 | <your name> | Add. Growing transcript across files"

Then bring the day onto your local `main` and tag it:

    git checkout main
    git merge day-02-transcript
    git tag day-02

**What each part does:**

- `git add -A` stages every new and changed file; anything `.gitignore` lists is skipped.
- `git commit -m "..."` records them as one commit, in the series' commit format from Day 00, Step 12; `Add` because the transcript is a new feature.
- `git checkout main` switches back to the main branch.
- `git merge day-02-transcript` brings today's commit onto `main`. Because `main` has not moved since
  you branched, git simply moves `main` forward to your commit (a **fast-forward**), with no
  extra merge commit. If `main` already contains the branch, it prints `Already up to date.`
  and changes nothing.
- `git tag day-02` puts a local bookmark on the finished day, so `git diff day-01 day-02`
  shows exactly what today changed.

**Check it:** `git log --oneline -3` shows today's commit at the top, on `main`, with
`tag: day-02` beside it.

## Check before you call it done

- The final answer refers to a file from an earlier turn by name
- `transcript.json` exists, is ignored by git, and alternates user/assistant after the system message
- You can state, out loud, why sending three files costs more than three times one file
