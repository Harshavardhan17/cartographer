# Tools and commands

Every tool and command you type while building cartographer, in one place. Each day's dev
notes list that day's commands in a table and link here the first time a tool appears, so
you can look up what a flag means without hunting back through earlier days.

You do not need to read this page top to bottom. Use it when a command in the notes is
unfamiliar, or when you want to remember what a flag you typed last week actually did.

**The project toolchain:** [uv](#uv) · [python](#python) · [pytest](#pytest) · [ruff](#ruff) · [mypy](#mypy)
**Version control:** [git](#git) · [GitHub Actions](#github-actions)
**The terminal:** [shell](#shell) · [files](#files) · [grep](#grep) · [diff](#diff)
**The model and the protocol:** [openrouter](#openrouter) · [mcp-inspector](#mcp-inspector) · [claude](#claude)
**What you build:** [cartographer](#cartographer)
**Libraries the project depends on:** [httpx](#httpx) · [mcp-sdk](#mcp-sdk) · [langgraph](#langgraph) · [sqlite](#sqlite) · [sqlite-vec](#sqlite-vec) · [model2vec](#model2vec) · [opentelemetry](#opentelemetry)

A note on reading commands. Text after `#` on a command line is a comment for you; the shell
ignores it. `"$CARTOGRAPHER_TARGET"` is the path of your pinned clone of click (set up on
Day 00), and the double quotes keep it in one piece if the path ever contains a space.

---

<a id="uv-run"></a><a id="uv-venv"></a><a id="uv-pip"></a><a id="uv-add"></a><a id="uv-sync"></a><a id="pip"></a><a id="venv"></a>

## uv

uv is a Python package and project manager: it creates the isolated environment your project
runs in and installs packages into it, much faster than `pip`. Almost every command in the
series starts with `uv run`, which is how you make sure the command uses the project's own
Python and packages rather than whatever is installed system-wide.

| Command | What it does |
|---|---|
| `uv --version` | Prints uv's version. If it prints nothing, uv is not installed yet. |
| `uv venv` | Creates the **virtual environment** in `.venv/`: a private copy of Python with its own packages, so this project cannot break, or be broken by, any other. |
| `uv pip install -e ".[dev]"` | Installs the project into `.venv`. `-e` (editable) links your source folder instead of copying it, so code changes take effect without reinstalling. `".[dev]"` means "this folder, plus the optional `dev` group" (pytest, ruff, mypy). The quotes stop the shell treating the brackets as a pattern. |
| `uv run <command>` | Runs a command inside the project's environment. `uv run pytest`, `uv run python -m ...` and so on. |
| `uv add "<package>>=X,<Y"` | Installs a package *and* writes it into `pyproject.toml` and `uv.lock`, so the dependency is recorded rather than only present on your machine. The version range keeps you on a release line the code was written against. |
| `uv sync` | Makes the environment match `pyproject.toml` and the lock file exactly. Run it when an import fails for a package you know is listed. |

First appears: Day 00.

---

<a id="python-m"></a><a id="python3"></a><a id="python-c"></a><a id="json-tool"></a><a id="json"></a>

## python

Python is the language the whole project is written in; the series pins Python 3.12. You
mostly run it through uv (`uv run python ...`) so it sees the project's packages.

| Command | What it does |
|---|---|
| `uv run python -m cartographer.<module>` | Runs one of the project's modules as a script. `-m` means "find this module on the import path and run it", which works from the repo root because the package is installed. Each module's `if __name__ == "__main__":` block is what runs. |
| `uv run python -m cartographer.<module> --flag value` | The same, with arguments the module reads itself (for example `--resume`, `--approve`, `--runs 3`). Each day's notes say what the flags mean. |
| `uv run python -c "<code>"` | Runs a few lines of Python given on the command line. The series uses it for quick checks: import a module, print one value, confirm it is what you expect. |
| `python3 -c "import tomllib; ..."` | The same with the system Python, used on Day 00 to check `pyproject.toml` parses before any environment exists. |
| `python3 -m json.tool <file>` | Pretty-prints a JSON file with indentation, so a saved transcript or response is readable. |

First appears: Day 00.

---

<a id="pytest-q"></a><a id="tests"></a><a id="monkeypatch"></a>

## pytest

pytest is the test runner: it finds every `test_*.py` file under `tests/`, runs each
`test_*` function, and reports which assertions failed. The series writes real tests from the
first week, and most of them replace the model with a stub so they run offline and for free.

| Command | What it does |
|---|---|
| `uv run pytest -q` | Runs every test. `-q` (quiet) prints one character per test and a summary line, instead of a line per test. |
| `uv run pytest -q tests/test_<name>.py` | Runs only the tests in one file. Faster while you work on that file. |
| `uv run pytest -q -s -k <word>` | `-k <word>` runs only tests whose names contain that word. `-s` lets the test's `print` output through to your terminal instead of capturing it. |

`monkeypatch` is a pytest fixture you will see in many tests: a parameter pytest hands the
test that can temporarily replace a function, an attribute or an environment variable, and
puts the original back when the test ends.

First appears: Day 00.

---

<a id="ruff-check"></a><a id="ruff-format"></a><a id="lint"></a>

## ruff

ruff is a linter and formatter for Python. The linter flags likely mistakes (unused imports,
undefined names, lines over the 100-character limit set in `pyproject.toml`), and the formatter rewrites your files into one
consistent layout so you never argue about style.

| Command | What it does |
|---|---|
| `uv run ruff check .` | Lints every Python file under the current folder (`.`). Prints each problem with file and line, or `All checks passed!`. |
| `uv run ruff check <file>` | Lints only the files you name. |
| `uv run ruff format .` | Reformats every Python file in place. Run it before you commit; it changes layout, never behaviour. |

First appears: Day 00 (installed and configured), run by hand from Day 01.

---

<a id="type-check"></a><a id="types"></a>

## mypy

mypy is a static type checker: it reads your type hints (`def read(path: str) -> str`) and
reports places where the code would pass the wrong kind of value, without running anything.
It catches a whole class of bug before a test even starts. The project runs it in strict mode, which also insists every function has type hints.

| Command | What it does |
|---|---|
| `uv run mypy src` | Type-checks everything under `src/`. Prints `Success: no issues found` or one line per problem. |

First appears: Day 00 (installed and configured), run by hand from Day 01.

---

<a id="git-init"></a><a id="git-config"></a><a id="git-add"></a><a id="git-commit"></a><a id="git-log"></a><a id="git-status"></a><a id="git-show"></a><a id="git-branch"></a><a id="git-checkout"></a><a id="git-pull"></a><a id="git-push"></a><a id="git-tag"></a><a id="git-diff"></a><a id="git-grep"></a><a id="git-clone"></a><a id="git-rev-parse"></a><a id="git-check-ignore"></a><a id="git-remote"></a><a id="tags"></a><a id="day-tags"></a>

## git

git is version control: it records snapshots of your project (**commits**) so you can see what
changed, when, and go back. The series uses one branch per day, one commit per day, and a
local tag per day, so every day's code is a named point in history you can return to.

**Setting up**

| Command | What it does |
|---|---|
| `git init -b main` | Turns the current folder into a git repository whose first branch is called `main`. |
| `git config user.name "<your name>"` | Sets the author name for commits *in this repository only*. Without `--global`, it does not touch any other repository on your machine. |
| `git config user.email "<your email>"` | Same, for the author email. Run it without a value to read back what is set. |
| `git clone --branch 8.5.0 <url> <folder>` | Downloads a repository into a folder, checked out at the release tagged `8.5.0` instead of the latest code. This is how the target is pinned. |
| `git remote add origin <url>` | Records the address of a repository on GitHub under the short name `origin`. Optional in the series; only needed to put your copy online. |
| `git push -u origin main` | Uploads your commits to `origin`. `-u` remembers that local `main` tracks `origin/main`, so later a bare `git push` knows where to go. |
| `git clone --depth 1 <url> <folder>` | Downloads only the latest commit, without the history. Enough for a one-off scan. `--quiet` hides the progress output. |

**Every day**

| Command | What it does |
|---|---|
| `git checkout main` | Switches to the `main` branch. |
| `git pull` | Brings `main` up to date with the remote, if you have one. Harmless if you do not. |
| `git checkout -b day-NN-<topic>` | Creates a new branch for today's work and switches to it. `-b` means "create". |
| `git branch --show-current` | Prints the branch you are on. A quick check before you start editing. |
| `git status --short` | Lists changed and untracked files, one per line with a two-letter code (`M` modified, `??` untracked). |
| `git diff main --stat` / `git diff --stat` | Summarises what changed: one line per file, with counts of added and removed lines. Without `--stat` it shows the changes themselves. |
| `git add -A` | Stages every new, changed and deleted file, except what `.gitignore` excludes. **Staging** means "include this in the next commit". |
| `git commit -m "Day-NN \| <your name> \| <Action>. <message>"` | Records the staged files as one commit with that message. The series uses one format: the day, your name, one action out of `Add`, `Update`, `Refactor`, `Delete` or `Fix` followed by a full stop, then a short plain message, such as `Day-06 \| <your name> \| Add. Tool calling loop`. One line, no body. |
| `git log --oneline` | Shows the history, one commit per line. |
| `git log --format='%an <%ae>'` | Prints each commit's author name and email, to confirm every commit is under your identity. |
| `git show --stat HEAD` | Shows the files in the latest commit. `HEAD` means "the commit you are on". |
| `git tag day-NN` | Puts a name on the commit you are on, so you can return to exactly today's code later. Every day ends with one. |
| `git tag -l` | Lists your tags. |
| `git checkout -- <file>` | Throws away your uncommitted changes to that one file and restores the committed version. Use it with care: the changes are gone. |

**Looking around**

| Command | What it does |
|---|---|
| `git -C <folder> <command>` | Runs a git command as if you were inside that folder. The daily readiness check uses it on the target. |
| `git -C "$CARTOGRAPHER_TARGET" rev-parse HEAD` | Prints the full commit id (the **SHA**) the target is on. It must be `8b19813f2bfca99f1018a587a8cf54fc959f2e5d`. |
| `git grep -n "<text>"` | Searches every file git tracks for the text and prints matches with line numbers (`-n`). Unlike plain `grep`, it skips untracked files, which makes it the right check for "did a secret reach the repository". |
| `git check-ignore <path>` | Prints the path if `.gitignore` excludes it, and nothing if it would be tracked. A way to confirm a generated file will never be committed. |

**Using day tags to get unstuck.** If you have the reference repository, `git checkout day-07`
puts the exact code Day 07 describes in your folder, and `git diff day-06 day-07` shows exactly
what one day changed. `git checkout main` takes you back.

First appears: Day 00.

---

<a id="ci"></a><a id="actions"></a><a id="workflow"></a>

## github-actions

GitHub Actions is GitHub's **CI** (continuous integration) service: every time you push, it
starts a fresh machine on GitHub's servers, installs your project there and runs the same
lint, type checks and tests you run by hand. It catches the day you forgot to run them, and
anything that only worked because of something left over on your laptop.

The recipe is a YAML file in `.github/workflows/`; the project's is `.github/workflows/ci.yml`,
written on Day 00. GitHub reads every file in that folder. Nothing runs it on your machine:
it only runs once your copy of the repository is on GitHub, and locally the same commands
(`uv run ruff check .`, `uv run mypy src`, `uv run pytest -q`) are what it runs.

**Reading a run.** Open the repository on GitHub and click the **Actions** tab. Each push
appears as one run: a yellow dot while it runs, a green tick if every step passed, a red cross
if one failed. Click a run, then a step, to see that step's output exactly as a terminal would
have printed it. The first red step is the one to fix; the steps after it never ran.

First appears: Day 00 (optional: it needs your copy on GitHub).

---

<a id="zsh"></a><a id="bash"></a><a id="terminal"></a><a id="echo"></a><a id="export"></a><a id="source"></a><a id="read"></a><a id="unset"></a><a id="env"></a><a id="test"></a><a id="printf"></a><a id="tee"></a><a id="sort"></a><a id="environment-variables"></a><a id="pipes"></a>

## shell

The shell is the program that reads what you type in a terminal and runs it; on macOS it is
zsh, and on most Linux machines it is bash. Most commands in the series work the same in both;
where they differ, the notes say so.

| Command | What it does |
|---|---|
| `echo "$NAME"` | Prints a value. `echo "$CARTOGRAPHER_TARGET"` is the first line of every day's readiness check. |
| `echo 'export NAME="value"' >> ~/.zshrc` | Appends one line to your shell's startup file (`~/.bashrc` for bash). `>>` appends; a single `>` would overwrite the whole file. |
| `source ~/.zshrc` | Re-reads the startup file in this terminal, so a new variable exists now rather than only in terminals you open later. |
| `export NAME="value"` | Sets an **environment variable**: a named value the shell hands to every program it starts. That is how the code finds the API key and the target path. |
| `read -rs "?OpenRouter key: " k` | Prompts for a value and stores it in the variable `k` without showing it on screen (`-s`) and without treating backslashes specially (`-r`). In bash: `read -rsp "OpenRouter key: " k`. Used so the key never appears in your shell history. |
| `unset k` | Deletes the variable `k`, so the key is not left lying around under a second name. |
| `test -n "$NAME"` | Succeeds if the variable is non-empty. Combined with `&& echo ok`, a quick "is it set?" check. |
| `env -u NAME <command>` | Runs one command with that variable removed, to prove the code fails loudly when it is missing. |
| `printf '<text>' >> <file>` | Writes exact text, including newlines (`\n`), to a file. Used to plant a test case. |
| `<command> 2>&1 \| tee <file>` | `2>&1` merges error output into normal output; `\| tee <file>` shows it on screen and saves a copy to the file. |
| `<command> \| sort -u` | Sorts the lines and removes duplicates (`-u`, unique). |
| `<a> && <b>` | Runs `b` only if `a` succeeded. |

First appears: Day 00.

---

<a id="cd"></a><a id="mkdir"></a><a id="ls"></a><a id="cp"></a><a id="mv"></a><a id="rm"></a><a id="cat"></a><a id="head"></a><a id="tail"></a><a id="find"></a><a id="touch"></a>

## files

The everyday commands for moving around and handling files. They are part of every Unix-like
system, so there is nothing to install.

| Command | What it does |
|---|---|
| `cd <folder>` | Changes the current folder. Most steps say which folder to run in. |
| `mkdir -p <folder>` | Creates a folder, and any missing parent folders (`-p`). No error if it already exists. |
| `touch <file>` | Creates an empty file, or updates the timestamp of an existing one. |
| `ls -l <path>` | Lists files with details: permissions, size, date. |
| `cat <file>` | Prints a file. `cat > <file> <<'EOF'` ... `EOF` writes everything between the two markers into the file. |
| `head -3 <file>` / `tail -3 <file>` | Prints the first, or last, three lines. `<command> \| tail -3` keeps only the last three lines of a command's output. |
| `cp <from> <to>` | Copies a file. `cp -R` copies a whole folder. |
| `mv <from> <to>` | Moves or renames a file. |
| `rm -f <file>` | Deletes a file, with no error if it is not there (`-f`). There is no undo. |
| `find . -path ./.git -prune -o -print` | Lists every file under the current folder, skipping the `.git` folder. |

First appears: Day 00.

---

<a id="grep-c"></a><a id="search"></a>

## grep

grep searches text for a pattern and prints the lines that match. The series uses it to count
things in generated maps and to check that output contains, or does not contain, a phrase.

| Command | What it does |
|---|---|
| `grep -n "<text>" <file>` | Prints matching lines with their line numbers (`-n`). |
| `grep -c "<pattern>" <file>` | Prints only how many lines match (`-c`, count). |

For searching your own repository, prefer [git grep](#git), which skips untracked files.

First appears: Day 01.

---

<a id="compare"></a>

## diff

diff compares two files line by line and prints what differs. Lines starting `<` are only in
the first file, lines starting `>` only in the second.

| Command | What it does |
|---|---|
| `diff <file-a> <file-b>` | Shows how two outputs differ, for example two maps generated with different tools. Prints nothing if the files are identical. |

First appears: Day 08.

---

<a id="api-key"></a><a id="openrouter-api-key"></a><a id="model"></a><a id="models"></a>

## openrouter

OpenRouter is a service that gives one endpoint, `https://openrouter.ai/api/v1`, for many
language models, speaking the same request format as OpenAI's API. The series uses its free
tool-calling models, so you can build everything without paying; which models are free
changes often, so check what is free today rather than trusting a model id from a post.

How the key is handled, every day:

| Command | What it does |
|---|---|
| `read -rs "?OpenRouter key: " k && export OPENROUTER_API_KEY="$k" && unset k` | Prompts for your key without echoing it, exports it for this terminal only, and deletes the temporary copy. The key is never written to any file, and `.env` stays empty. |
| `test -n "$OPENROUTER_API_KEY" && echo ok` | Confirms the key is loaded in this terminal. Open a new terminal and you must load it again; that is deliberate. |

The code reads it as `os.environ["OPENROUTER_API_KEY"]`, which fails loudly with a `KeyError`
if you forgot, rather than sending an unauthenticated request.

First appears: Day 01.

---

<a id="mcp"></a><a id="mcp-dev"></a><a id="inspector"></a><a id="mcp-cli"></a>

## mcp-inspector

The MCP Inspector is the official browser-based client for testing an MCP server: it lists your
server's tools, resources and prompts, lets you call them by hand, and shows the raw JSON going
over the wire. You start it through the `mcp` command that the `mcp[cli]` package installs.

| Command | What it does |
|---|---|
| `uv run mcp dev src/cartographer/server.py` | Starts the inspector and launches your server file as a subprocess for it to talk to over **stdio** (standard input and output). It opens a browser tab. |
| `CARTOGRAPHER_ROOT="$CARTOGRAPHER_TARGET" uv run mcp dev src/cartographer/server.py` | The same, with an environment variable set for that one command only, so the server knows which repository to expose. |

The inspector interface is a separate program that `mcp dev` fetches and starts. If the
command fails before a browser opens, read its error output: it names what it could not find.
Stop it with Ctrl-C in the terminal.

First appears: Day 09.

---

<a id="claude-cli"></a><a id="claude-code"></a><a id="claude-mcp"></a><a id="editor"></a><a id="mcp-client"></a>

## claude

`claude` is the command-line program for Claude Code, one of the editors and agents that can act
as an MCP client. The series uses it to show a real client calling your server; any MCP client
works, and the notes say where the steps differ.

| Command | What it does |
|---|---|
| `claude mcp add cartographer -- <absolute path to .venv/bin/cartographer-mcp>` | Registers your server under the name `cartographer`. Everything after `--` is the command the client runs to start it. Use the full absolute path, spelled out. |
| `claude mcp list` | Lists every registered server and its command. Check the path character by character. |
| `claude` | Starts an interactive session, where you can ask questions that the client answers by calling your server's tools. |

First appears: Day 11.

---

<a id="cartographer-cli"></a><a id="cartographer-mcp"></a><a id="cartographer-map"></a>

## cartographer

The project you are building also becomes two commands once `[project.scripts]` in
`pyproject.toml` declares them and the package is installed. They are thin entry points into
the same code the `python -m` commands run.

| Command | What it does |
|---|---|
| `.venv/bin/cartographer-mcp` | Starts cartographer as an MCP server over stdio. You do not usually run it yourself; an MCP client starts it. |
| `uv run cartographer` | With no arguments, prints the usage block and exits non-zero. `echo $?` straight afterwards prints that exit status. |
| `uv run cartographer map "$CARTOGRAPHER_TARGET"` | Scans a repository and produces its map, pausing for your approval before anything is written. |
| `uv run cartographer status "$CARTOGRAPHER_TARGET"` | Shows where a paused scan is. |
| `uv run cartographer approve "$CARTOGRAPHER_TARGET"` | Approves the paused map, which lets it be written. |
| `uv run cartographer reject "$CARTOGRAPHER_TARGET"` | Rejects it; nothing is written. |

First appears: Day 11 (`cartographer-mcp`), Day 21 (`cartographer`).

---

<a id="http"></a>

## httpx

httpx is a Python HTTP client: the library that sends the request to the model and reads the
response. Week one uses it directly, with no AI SDK, so you see exactly what goes over the wire.

Installed with the project (`uv pip install -e ".[dev]"`). First appears: Day 00 (declared),
Day 01 (used).

---

<a id="mcpserver"></a><a id="mcp-python-sdk"></a>

## mcp-sdk

The official MCP Python SDK, installed as `mcp[cli]`; the `[cli]` extra adds the `mcp` command.
Its `MCPServer` class is what turns ordinary Python functions into tools, resources and prompts
a client can discover.

Declared in `pyproject.toml` as `"mcp[cli]>=2.2,<3"`. First appears: Day 09.

---

<a id="langgraph-checkpoint-sqlite"></a><a id="checkpointer"></a><a id="graph"></a>

## langgraph

LangGraph is a library for building an agent as a **graph**: nodes that each do one job, edges
that decide what runs next, and a shared state object passed between them. It is what lets the
agent branch, loop, survive a crash and pause for a human.

| Command | What it does |
|---|---|
| `uv add "langgraph>=1.2,<2"` | Adds LangGraph to the project, on the 1.x release line the code is written against. |
| `uv add langgraph-checkpoint-sqlite` | Adds the checkpointer that saves graph state to a SQLite file, so a killed run can resume. |

First appears: Day 15 (`langgraph`), Day 19 (the SQLite checkpointer).

---

<a id="sqlite3"></a><a id="database"></a>

## sqlite

SQLite is a complete database stored in a single file, with no server to run. Python ships with
it as the `sqlite3` module, so the series uses it for the checkpointer, for memory and for the
search index without installing anything extra.

| Command | What it does |
|---|---|
| `rm -f .cartographer/scans.sqlite` | Deletes the saved scans so the next run starts clean. |
| `git check-ignore .cartographer/scans.sqlite` | Confirms the database file is ignored by git and can never be committed. |

First appears: Day 19.

---

<a id="vector-search"></a><a id="embeddings"></a>

## sqlite-vec

sqlite-vec is a SQLite extension that adds vector search: store a list of numbers for each piece
of code and ask for the nearest ones. It is what lets the agent search a repository by meaning
rather than by exact words.

Installed with `uv add sqlite-vec model2vec`. First appears: Day 23.

---

<a id="embedder"></a>

## model2vec

model2vec is a small, fast library that turns text into **embeddings**, the lists of numbers
that sqlite-vec searches. It runs on your machine, so building the index costs nothing per call.

Installed with `uv add sqlite-vec model2vec`. First appears: Day 23.

---

<a id="otel"></a><a id="otlp"></a><a id="opentelemetry-sdk"></a><a id="tracing"></a><a id="spans"></a>

## opentelemetry

OpenTelemetry is the open standard for tracing a program: it records **spans**, timed records of
one piece of work each, nested to show what called what. OTLP is its wire format, which most
trace viewers can read.

| Command | What it does |
|---|---|
| `uv add "opentelemetry-sdk>=1.44,<2"` | Adds the OpenTelemetry SDK to the project. |
| `uv add opentelemetry-exporter-otlp-proto-http` | Optional: adds the exporter that sends spans over HTTP in OTLP format to a trace viewer you run yourself. |

First appears: Day 26.
