# Day 01: Why your first agent should be 40 lines, not a framework

Dev notes for this day's post: [read the post](https://harshakatkam.dev/the-40-line-agent).
Step numbers follow the full build guide; steps only the repository owner needs, such as publishing to GitHub, are left out. New here? Start with [how to use these notes](README.md).

---

**Today's build:** the bare loop

Starting point: yesterday's scaffold. `~/workspace/personal/cartographer` on `main`, `pyproject.toml` with
`httpx` as the only runtime dependency, `src/cartographer/__init__.py` holding only
`__version__`, one passing test.

Today it makes its first model call. One hardcoded file, one HTTP request, prose out.
No SDK, no framework, no abstraction you cannot read in one sitting.

Time: about 30 minutes.

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
| `src/cartographer/agent.py` | New | The whole agent: reads one file, sends it to a model in one HTTP request, prints the reply |
| `tests/test_agent.py` | New | An offline test that the prompt carries the file's contents and permits "I cannot tell" |

## Commands and tools today

| Command | What it does |
|---|---|
| `echo "$CARTOGRAPHER_TARGET"` | Readiness check, part one: prints the target's path |
| `git -C "$CARTOGRAPHER_TARGET" rev-parse HEAD` | Readiness check, part two: prints the target's commit |
| `cd ~/workspace/personal/cartographer` | Moves to the repo root, where every command today runs |
| `git checkout main` | Switches to the main branch |
| `git checkout -b day-01-bare-loop` | Creates today's branch and switches to it |
| `git branch --show-current` | Prints the branch you are on |
| `read -rs "?OpenRouter key: " k && export OPENROUTER_API_KEY="$k" && unset k` | Reads your API key without echoing it and puts it in this terminal's environment, never in a file (zsh; bash uses `read -rsp "OpenRouter key: " k`) |
| `test -n "$OPENROUTER_API_KEY" && echo set` | Confirms the key is loaded without printing it |
| `uv run python -c "import cartographer.agent as agent; print(agent.MODEL)"` | Imports the new module without running it, proving it has no syntax errors |
| `uv run pytest -q` | Runs the tests |
| `uv run python -m cartographer.agent` | Runs the agent: one real model call about one file |
| `env -u OPENROUTER_API_KEY uv run python -m cartographer.agent` | Runs it with the key removed, to see what a missing key looks like |
| `OPENROUTER_API_KEY=not-a-key uv run python -m cartographer.agent` | Runs it with a wrong key, to see what a `401` looks like |
| `uv run ruff check . && uv run ruff format .` | Lints every file, then rewrites them into ruff's standard formatting |
| `uv run mypy src` | Type-checks the package in strict mode |
| `git add -A` | Stages every new and changed file |
| `git commit -m "..."` | Records today's work as one commit |
| `git merge day-01-bare-loop` | Brings today's branch onto `main` |
| `git tag day-01` | Bookmarks the finished day |
| `git log --oneline -3` | Shows the last three commits |
| `git grep OPENROUTER_API_KEY` | Searches every tracked file, to confirm no key reached the repository |

New tools today: [openrouter](TOOLS.md#openrouter)

## Step 1 — Start a branch for today

**Where:** the repo root, `~/workspace/personal/cartographer`.
**Why this step exists:** every day's work goes on its own branch and is merged the same
day, so each day is one readable diff in the history.

**Run this:**

    cd ~/workspace/personal/cartographer
    git checkout main
    git checkout -b day-01-bare-loop

**What each part does:** `cd` moves to the repo root; `git checkout main` switches to the
main branch, which holds every finished day; `git checkout -b day-01-bare-loop` creates today's
branch from it and switches to it (`-b` is "create, then switch").

**Check it:** `git branch --show-current` prints `day-01-bare-loop`.

## Step 2 — Get a key into the environment, not into a file

**Where:** the same terminal you will run the agent from.
**Why this step exists:** the model is reached through **OpenRouter**, one web address that
forwards requests to hundreds of models. Every request must carry your **API key**, a
secret string that identifies your account. It must never be written into any file in the
repo.

Create a key in your OpenRouter account settings, then:

**Run this:**

    read -rs "?OpenRouter key: " k && export OPENROUTER_API_KEY="$k" && unset k

`read -rs` keeps the key off the screen and out of shell history. Nothing in the repo ever writes it down —
`.env` has been in `.gitignore` since the first commit and stays empty.

**What each part does:**

- `read` waits for you to type a line and stores it in a shell variable, here `k`.
- `-r` keeps backslashes as typed; `-s` (silent) stops the characters echoing to the screen,
  so the key is never visible and never lands in your scrollback.
- `"?OpenRouter key: "` is the prompt text. The leading `?` is **zsh** syntax for "show this
  prompt". In bash, write `read -rsp "OpenRouter key: " k` instead.
- `export OPENROUTER_API_KEY="$k"` copies the value into an **environment variable**: a
  named value the shell hands to every program it starts. That is how the Python code will
  find the key without it ever being written down.
- `unset k` deletes the temporary variable, so only the exported copy remains.

The variable lives only in this terminal. Open a new one and you repeat this step.

**Check it:**

    test -n "$OPENROUTER_API_KEY" && echo set

It should print `set` without printing the key itself.

## Step 3 — Write the agent, `src/cartographer/agent.py`

**Where:** `src/cartographer/agent.py` — new file.
**Why this file exists:** it is the whole agent. Forty lines including blanks. Over the
next six days it grows, but it stays the place where the model is called.

**Add this code:**

    import os
    import pathlib
    import sys

    import httpx

    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    MODEL = os.environ.get("CARTOGRAPHER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")
    TARGET = pathlib.Path("src/cartographer/agent.py")

    PROMPT = """You are reading one file from a repository you have never seen.

    Say what this file is for, what it depends on, and what would break if it
    were deleted. Where the file does not say, answer that you cannot tell.

    --- {path} ---
    {source}
    """

    def ask(prompt: str) -> str:
        response = httpx.post(
            OPENROUTER_URL,
            headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
            json={"model": MODEL, "messages": [{"role": "user", "content": prompt}]},
            timeout=120.0,
        )
        response.raise_for_status()
        body = response.json()
        return str(body["choices"][0]["message"]["content"])

    def main() -> None:
        if not TARGET.exists():
            sys.exit(f"cannot find {TARGET} from {pathlib.Path.cwd()}")
        print(ask(PROMPT.format(path=TARGET, source=TARGET.read_text())))

    if __name__ == "__main__":
        main()

**What each part does:**

*The imports.* `os` reads environment variables, `pathlib` handles file paths as objects
rather than strings, and `sys` lets the program exit with a message. Those three are the
standard library. After a blank line (the convention that separates standard library from
third-party imports) comes `httpx`, the one installed dependency, which sends the HTTP
request.

*The three constants.* Upper-case names are module-level settings that never change while
the program runs.

- `OPENROUTER_URL` is the **chat completions endpoint**: the address that takes a list of
  messages and returns the model's reply. OpenRouter speaks the same request shape the
  OpenAI API uses, which is why the path ends in `chat/completions`.
- `MODEL` is the model id, read from the `CARTOGRAPHER_MODEL` environment variable if you set
  one, otherwise the default after the comma. `os.environ.get(name, default)` returns the
  default instead of failing when the variable is missing. Free-tier availability churns;
  check which tool-calling models are free today and set the variable rather than editing
  the source.
- `TARGET` is the one file the agent reads: its own source. It is a path relative to the
  repo root, which is why you must run the agent from there.

*The prompt.* `PROMPT` is a triple-quoted string, so it can span lines. It is a template:
`{path}` and `{source}` are placeholders that `.format()` fills in later. The instructions
ask three concrete questions (purpose, dependencies, what breaks) and, crucially, give the
model permission to say "I cannot tell". Without that line a model fills gaps with
plausible guesses. The `--- {path} ---` line labels where the file begins, so the model can
tell instructions from file contents.

*`ask(prompt)`, the model call.* This is the entire mechanism of a **model call**: text in,
text out, over HTTP.

- `httpx.post(...)` sends one HTTP POST request and waits for the answer.
- The first argument is the URL.
- `headers={"Authorization": f"Bearer ..."}` attaches the key in the standard form
  `Bearer <key>`. `os.environ['OPENROUTER_API_KEY']` uses square brackets on purpose: if the
  variable is missing it raises `KeyError` right here, instead of quietly sending an empty
  key.
- `json={...}` is the request body, which httpx converts to JSON. It has exactly two fields:
  `"model"`, which model to use, and `"messages"`, a list of messages. Each message is a
  `role` (who is speaking: `user` is you) and `content` (the text). Today the list holds one
  message.
- `timeout=120.0` waits up to two minutes. Free models can be slow, and httpx's default of
  five seconds would cut most answers off.
- `response.raise_for_status()` turns an HTTP error status (`401` bad key, `429` rate limit,
  `5xx` server trouble) into an exception that names the status. Without it a `401` or `429`
  surfaces as `KeyError: 'choices'`, which sends you looking in the wrong place.
- `body = response.json()` parses the reply body from JSON into Python dictionaries and
  lists.
- `body["choices"][0]["message"]["content"]` digs out the answer. The response holds a list
  of `choices`; you asked for one, so you take item `0`; inside it is the reply `message`,
  and its `content` is the text.
- `str(...)` around it. `response.json()` is typed as `Any`, and `mypy --strict` in CI
  rejects returning `Any` from a function annotated `-> str`.

*`main()`, the program.* `if not TARGET.exists()` checks the file is reachable before
spending a request, and `sys.exit(...)` stops with a message that prints both the path and
the directory you ran from, which is the information you need to fix it. Then the last line
reads the file (`TARGET.read_text()`), fills the template (`PROMPT.format(...)`), sends it
(`ask(...)`) and prints the reply.

*The guard.* `if __name__ == "__main__": main()` runs `main` only when the file is executed
as a program. When a test imports the module, `__name__` is `"cartographer.agent"` instead,
so nothing runs and no request is sent.

**Check it:**

    uv run python -c "import cartographer.agent as agent; print(agent.MODEL)"

It prints the model id without making a request, because importing the module does not run
`main`. A `SyntaxError` here usually means the triple-quoted `PROMPT` lost a quote.

## Step 4 — A test that does not touch the network

**Where:** `tests/test_agent.py` — new file.
**Why this file exists:** the model's answer cannot be tested, but what you send it can.

**Add this code:**

    from cartographer.agent import PROMPT

    def test_prompt_carries_the_source_and_permits_uncertainty() -> None:
        filled = PROMPT.format(path="src/cartographer/agent.py", source="VALUE = 1")
        assert "VALUE = 1" in filled
        assert "cannot tell" in filled

**What each part does:**

- `from cartographer.agent import PROMPT` imports only the template. Importing the module
  does not call `main`, thanks to the guard, so no network request happens.
- `filled = PROMPT.format(...)` fills the template exactly as `main` does, with a fake path
  and a one-line fake source.
- `assert "VALUE = 1" in filled` proves the file contents reach the text sent to the model.
  Rename a placeholder in one place and not the other, and this fails.
- `assert "cannot tell" in filled` proves the permission to be uncertain is still in the
  prompt.

Small, but it is the real contract of the day: the file contents reach the model, and
the model is told it is allowed to not know. Both are things you can break by accident.

**Check it:**

    uv run pytest -q

`2 passed`: this test plus yesterday's version test.

## Step 5 — Run it

**Where:** the repo root, because `TARGET` is a relative path.
**Why this step exists:** this is the first real model call.

**Run this:**

    uv run python -m cartographer.agent

**What each part does:** `uv run` uses the project's environment; `python -m
cartographer.agent` runs the module by its import name rather than by file path, which is
how a package's modules are meant to be run.

**Check it:** it reads itself and describes itself. That is a useful first target: you know
the right answer, so you can judge the output immediately. A paragraph about a script that
reads one file and sends it to a model means it worked.

Then check the boring paths actually behave:

    env -u OPENROUTER_API_KEY uv run python -m cartographer.agent   # KeyError, loudly
    OPENROUTER_API_KEY=not-a-key uv run python -m cartographer.agent  # 401 from raise_for_status

- `env -u OPENROUTER_API_KEY ...` runs the command with that variable removed, so you see
  what a missing key looks like: a `KeyError` naming `OPENROUTER_API_KEY`.
- `OPENROUTER_API_KEY=not-a-key ...` sets the variable for that one command only, so you
  see what a wrong key looks like: an `HTTPStatusError` mentioning `401`.

Both should fail fast with something that names the cause.

## Step 6 — Lint, types, tests

**Where:** the repo root.
**Why this step exists:** it runs locally exactly what CI will run on GitHub, so a red CI is
never a surprise.

**Run this:**

    uv run ruff check . && uv run ruff format .
    uv run mypy src
    uv run pytest -q

**What each part does:**

- `ruff check .` lints every file; `ruff format .` rewrites files into ruff's standard
  formatting (spacing, quotes, line breaks), so formatting is never a review topic.
- `mypy src` type-checks the package in strict mode. If it complains about returning `Any`,
  the `str(...)` in `ask` is missing.
- `pytest -q` runs both tests.

**Check it:** ruff prints `All checks passed!`, mypy prints `Success: no issues found`, and
pytest prints `2 passed`.

## Step 7 — Commit, merge and tag the day

**Where:** the repo root.
**Why this step exists:** the day is not done until it is committed, on `main`, and tagged.

**Run this:**

    git add -A
    git commit -m "Day-01 | <your name> | Add. Forty-line agent that describes one file"

Then bring the day onto your local `main` and tag it:

    git checkout main
    git merge day-01-bare-loop
    git tag day-01

**What each part does:**

- `git add -A` stages every new and changed file; anything `.gitignore` lists is skipped.
- `git commit -m "..."` records them as one commit, in the series' commit format from Day 00, Step 12; `Add` because the day adds something new.
- `git checkout main` switches back to the main branch.
- `git merge day-01-bare-loop` brings today's commit onto `main`. Because `main` has not moved since
  you branched, git simply moves `main` forward to your commit (a **fast-forward**), with no
  extra merge commit. If `main` already contains the branch, it prints `Already up to date.`
  and changes nothing.
- `git tag day-01` puts a local bookmark on the finished day, so `git diff day-00 day-01`
  shows exactly what today changed.

**Check it:** `git log --oneline -3` shows today's commit at the top, on `main`, with
`tag: day-01` beside it.

## Check before you call it done

- `uv run python -m cartographer.agent` prints a description of `agent.py`
- `git grep OPENROUTER_API_KEY` matches only `src/cartographer/agent.py`, and nothing looks like a key literal
- The output is prose you cannot verify mechanically. That is the honest state of the
  project at the end of today and the post says so.

`git grep` searches only files git tracks, so it is the right tool for "did a secret reach
the repository".
