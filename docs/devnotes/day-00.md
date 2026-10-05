# Day 00: Learn AI agents by building one, in 30 days

Dev notes for this day's post: [read the post](https://harshakatkam.dev/pilot-thirty-days-one-agent).
Step numbers follow the full build guide; steps only the repository owner needs, such as publishing to GitHub, are left out. New here? Start with [how to use these notes](README.md).

---

**Today's build:** create the repo

No agent code today. The goal is a project that already works like a real one before a
single feature exists: installable, with a passing test, lint and type checks from the first commit.

Time: about 40 minutes. Everything below is copy-paste, and every command and every line
of every file is explained, so you know what each one is for rather than just that it is
there.

Before you start, two tools need to be installed: `git`, and `uv`. **uv** is a Python
package and project manager: it creates the isolated environment your project runs in and
installs packages into it, much faster than `pip`. The primer's checklist has you confirm
`uv --version` prints something; if it does not, install uv from its documentation first.

## Files you will touch today

| File | New or edited | What it is for |
|---|---|---|
| `pyproject.toml` | New | The project's identity card: its name, version, Python version, dependencies, and settings for the lint and type-check tools |
| `src/cartographer/__init__.py` | New | Marks `src/cartographer/` as an importable Python package, and holds the version number |
| `.gitignore` | New | Tells git which files never to track: the virtual environment, caches, secrets, generated output |
| `.github/workflows/ci.yml` | New | The CI recipe GitHub runs on every push: lint, type-check, test |
| `tests/test_package.py` | New | The first real test, proving the package imports and exposes a well-formed version |
| `~/workspace/personal/targets/click` | New, outside the repo | The target: a pinned clone of `pallets/click` 8.5.0 that the agent studies every day |
| `~/.zshrc` (or `~/.bashrc`) | Edited, outside the repo | Gains one line setting `CARTOGRAPHER_TARGET` to the target's path |

## Commands and tools today

| Command | What it does |
|---|---|
| `mkdir -p ~/workspace/personal/cartographer && cd ~/workspace/personal/cartographer` | Creates the project folder and moves your terminal into it |
| `git init -b main` | Turns the folder into a git repository whose first branch is `main` |
| `git status` | Shows which branch you are on and which files have changed |
| `git config user.name "<your name>"` | Sets the author name on this repository's commits only |
| `git config user.email "<your personal address>"` | Sets the author email on this repository's commits only |
| `git config user.email` | Prints the email back, so you can confirm it before the first commit |
| `mkdir -p src/cartographer tests` | Creates the package folder and the tests folder |
| `touch src/cartographer/__init__.py` | Creates the empty file that makes the folder an importable package |
| `find . -path ./.git -prune -o -print` | Lists every file and folder in the project, skipping git's own `.git` folder |
| `python3 -c "import tomllib; ..."` | Reads `pyproject.toml` with Python's TOML parser and prints the project name, proving the file is valid |
| `uv venv && uv pip install -e ".[dev]"` | Creates the project's private Python environment and installs the project, editable, with its developer tools |
| `uv run python -c "import cartographer, httpx; print('ok')"` | Runs Python inside that environment and proves both packages import |
| `git status --short` | The one-line-per-file form of `git status`, used to check `.gitignore` works |
| `mkdir -p .github/workflows` | Creates the folder GitHub Actions scans for CI workflow files |
| `cat .github/workflows/ci.yml` | Prints the CI file, so you can check its indentation |
| `uv run pytest -q` | Runs the tests, printing one dot per passing test |
| `uv run ruff check .` | Lints every file: flags likely bugs and style problems without running the code |
| `uv run mypy src` | Type-checks the package in strict mode |
| `git add -A` | Stages every new, changed and deleted file for the next commit |
| `git commit -m "..."` | Records the staged files as the first commit, in the series' commit format (Step 12) |
| `git tag day-00` | Puts a local bookmark named `day-00` on that commit, so you can return to or diff against today |
| `git log --oneline` | Shows the history, one commit per line |
| `git show --stat HEAD` | Lists the files the latest commit contains |
| `git remote add origin git@github.com:<your-github-username>/cartographer.git` | Optional: links your local repository to the empty one you created on your own GitHub account |
| `git push -u origin main` | Optional: uploads your commits to that repository, which starts the first CI run |
| `mkdir -p ~/workspace/personal/targets` | Creates the folder that holds the repositories the agent studies |
| `git clone --branch 8.5.0 https://github.com/pallets/click ~/workspace/personal/targets/click` | Downloads click and checks out the pinned 8.5.0 release |
| `git -C ~/workspace/personal/targets/click rev-parse HEAD` | Prints the exact commit you checked out, which must be `8b19813f...` |
| `echo 'export CARTOGRAPHER_TARGET=...' >> ~/.zshrc` | Appends one line to your shell's startup file so every terminal knows where the target lives |
| `source ~/.zshrc` | Re-reads the startup file in this terminal, so the variable exists now |
| `echo "$CARTOGRAPHER_TARGET"` | Prints the variable, the first half of the readiness check every later day opens with |
| `git -C "$CARTOGRAPHER_TARGET" rev-parse HEAD` | Prints the target's commit, the second half of the readiness check |

New tools today: [shell](TOOLS.md#shell), [files](TOOLS.md#files), [git](TOOLS.md#git), [uv](TOOLS.md#uv), [python](TOOLS.md#python), [pytest](TOOLS.md#pytest), [ruff](TOOLS.md#ruff), [mypy](TOOLS.md#mypy), [GitHub Actions](TOOLS.md#github-actions)

## Step 1 — Create the project folder and turn it into a git repository

**Where:** any terminal; the first command creates the folder and moves you into it.
**Why this step exists:** everything for the next thirty days lives in this one folder,
and git needs to be tracking it before there is anything to track.

**Run this:**

    mkdir -p ~/workspace/personal/cartographer && cd ~/workspace/personal/cartographer
    git init -b main

**What each part does:**

- `mkdir -p ~/workspace/personal/cartographer` creates the folder. `-p` means "make any
  missing parent folders too, and do not complain if it already exists", so the command is
  safe to run twice.
- `&&` runs the next command only if the previous one succeeded. If the folder could not be
  created, you do not `cd` somewhere unexpected.
- `cd ~/workspace/personal/cartographer` moves your shell into the new folder. Every later
  command in this file runs from here, which this series calls the **repo root**.
- `git init` turns the current folder into a git repository by creating a hidden `.git/`
  folder that stores the history. `-b main` names the first branch `main` instead of
  whatever your git version defaults to, so it matches GitHub's default.

**Check it:**

    git status

You should see `On branch main` and `No commits yet`. If you see `not a git repository`,
the `cd` did not happen; run the `cd` line again.

## Step 2 — Set your personal identity, for this repository only

**Where:** the repo root.
**Why this step exists:** every commit records a name and an email. Do this **before the
first commit**. A work email in a public repo's history is not something you can quietly
fix afterwards — it is in every clone.

**Run this:**

    git config user.name "<your name>"
    git config user.email "<your personal address>"

**What each part does:**

- `git config user.name "..."` sets the author name stamped on every commit. Replace the
  placeholder, angle brackets included, with your own name.
- `git config user.email "..."` sets the author email. Replace the placeholder, angle
  brackets included, with your personal address.
- Neither command has `--global`. Without it, git writes the setting into this repository's
  `.git/config` only, so it cannot leak into other projects on the same machine, and other
  projects' settings cannot leak into this one.

**Check it:** verify, and read the output rather than assuming:

    git config user.email

If that prints a work address, stop and fix it before continuing.

## Step 3 — Create the package folders

**Where:** the repo root.
**Why this step exists:** Python projects that will be published or installed keep their
code in a `src/` folder, separate from tests and configuration. It stops tests from
accidentally importing the loose folder instead of the installed package.

**Run this:**

    mkdir -p src/cartographer tests
    touch src/cartographer/__init__.py

**What each part does:**

- `mkdir -p` creates two folders in one go: `src/cartographer` (where all agent code will
  live) and `tests` (where the tests live).
- `touch src/cartographer/__init__.py` creates an empty file. A folder containing an
  `__init__.py` is a Python **package**: something you can `import cartographer` from. It
  stays empty until Step 11 gives it one line.

**Check it:**

    find . -path ./.git -prune -o -print

You should see `./src/cartographer/__init__.py` and `./tests` in the list.

## Step 4 — Write `pyproject.toml`

**Where:** `pyproject.toml` — new file at the repo root.
**Why this file exists:** it is the single place that says what this project is and what
it needs. `uv`, `pip`, `ruff` and `mypy` all read their settings from it.

**Add this code:**

    [project]
    name = "cartographer"
    version = "0.0.1"
    description = "An agent that maps an unfamiliar codebase"
    requires-python = ">=3.12"
    dependencies = ["httpx>=0.28"]

    [project.optional-dependencies]
    dev = ["pytest>=8", "ruff>=0.6", "mypy>=1.11"]

    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"

    [tool.ruff]
    line-length = 100

    [tool.ruff.lint]
    select = ["E4", "E7", "E9", "F"]

    [tool.mypy]
    python_version = "3.12"
    strict = true

**What each part does:**

The file is TOML: `[section]` headers, then `key = value` lines beneath them.

- `[project]` holds the standard package metadata every Python tool understands.
  - `name = "cartographer"` is the package name. It matches the folder `src/cartographer`,
    which is how the build tool finds the code without being told.
  - `version = "0.0.1"` is the release number in `major.minor.patch` form. It starts below
    `0.1` because nothing works yet.
  - `description` is the one-line summary shown by package indexes.
  - `requires-python = ">=3.12"` refuses to install on older Pythons, so nobody gets a
    confusing syntax error from a feature 3.12 introduced.
  - `dependencies = ["httpx>=0.28"]` lists what the code needs at runtime. **httpx** is an
    HTTP client library; it is how the agent will talk to the model over the network. It is
    the only runtime dependency for the whole first week, on purpose.
- `[project.optional-dependencies]` with `dev = [...]` defines an **extra**: a named group
  of packages installed only when asked for. These are the developer tools, which the agent
  itself never imports: `pytest` runs tests, `ruff` is a **linter** (a tool that flags
  likely bugs and style problems without running the code) and formatter, and `mypy` is a
  **type checker** (it reads your type hints and reports places where the types cannot
  line up). The `>=` versions are minimums, not pins.
- `[build-system]` tells installers how to turn the folder into an installable package.
  `requires = ["hatchling"]` names the build tool to download, and
  `build-backend = "hatchling.build"` names the function inside it to call. Hatchling is a
  small, standard choice; you never call it yourself.
- `[tool.ruff]` with `line-length = 100` lets lines run to 100 characters before ruff
  complains, instead of its default of 88.
- `[tool.ruff.lint]` with `select = [...]` names the lint rules to run: `F` is pyflakes
  (unused imports, undefined names, redefinitions) and the three `E` groups are the
  pycodestyle errors that are never a matter of taste. Naming the set matters because the
  `>=` minimum means you install the newest ruff, and newer releases switch on more rules
  by default; without this line, code that passed yesterday can fail after an upgrade.
- `[tool.mypy]` with `python_version = "3.12"` checks types against 3.12's rules, and
  `strict = true` switches on every optional check. Strict mode is what forces type hints
  on every function, which pays off later when message shapes change.

**Check it:**

    python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['name'])"

It should print `cartographer`. A `TOMLDecodeError` means a typo, usually a missing quote.

## Step 5 — Create the virtual environment and install the project

**Where:** the repo root.
**Why this step exists:** a **virtual environment** is a private folder of installed
packages for this one project, so its versions never collide with anything else on your
machine.

**Run this:**

    uv venv && uv pip install -e ".[dev]"

**What each part does:**

- `uv venv` creates the environment in a folder called `.venv/` at the repo root.
- `uv pip install` installs packages into that environment, with the same arguments `pip`
  takes.
- `-e` means **editable**: instead of copying your code into the environment, it links to
  `src/cartographer`, so every edit you make is live without reinstalling.
- `".[dev]"` means "the project in this folder (`.`), plus its `dev` extra". The quotes stop
  your shell from treating the square brackets as a filename pattern.

**Check it:**

    uv run python -c "import cartographer, httpx; print('ok')"

It should print `ok`. `ModuleNotFoundError: cartographer` means the editable install did
not happen; rerun the install line and read its output.

## Step 6 — Write `.gitignore`

**Where:** `.gitignore` — new file at the repo root.
**Why this file exists:** write this before anything is committed, so a key can never be
staged by accident. Git skips every path that matches a line in this file.

**Add this code:**

    .venv/
    __pycache__/
    *.pyc
    .env
    .mypy_cache/
    .pytest_cache/
    .ruff_cache/
    maps/

**What each part does:**

- `.venv/` — the virtual environment from Step 5. It is large, machine-specific, and
  rebuilt from `pyproject.toml` on any machine. A trailing `/` means "a folder with this
  name".
- `__pycache__/` and `*.pyc` — compiled bytecode Python writes next to your source to start
  faster. `*` matches any name, so `*.pyc` catches every such file.
- `.env` — the conventional file for secrets such as API keys. It is ignored from the very
  first commit so it is impossible to push one by accident. In this series it stays empty
  anyway: keys live only in your shell.
- `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/` — scratch folders the three dev tools
  create to run faster next time.
- `maps/` — where the agent will later write the maps it generates. They are output, not
  source, so they stay out of the history from the start.

**Check it:**

    git status --short

You should not see `.venv/` in the list. If you do, the file is misnamed; it must be
exactly `.gitignore`, with the leading dot.

## Step 9 — Add CI, from the first commit

**Where:** `.github/workflows/ci.yml` — new file. Create its folder first with
`mkdir -p .github/workflows`; the folder name is fixed by GitHub, which scans it for CI
recipes.
**Why this file exists:** **CI** (continuous integration) is an automatic run of the same
tests, lint and type checks you run by hand, on a fresh machine, every time you push. It is a
habit worth having from the first commit: the check happens even on the day you forget to
run it, and on a machine that has none of your laptop's leftovers. **GitHub Actions** is
GitHub's CI service; it reads every YAML file in `.github/workflows/` and runs it on GitHub's
servers. That means CI only runs once your copy of the repository is on GitHub (the optional
Step 12a shows how). Until then the file just sits in the repository, and the same three
commands it runs are the ones you run locally in Step 11.

**Add this code:**

    name: ci
    on: [push, pull_request]
    jobs:
      check:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v7
          - uses: astral-sh/setup-uv@v10.2.0
          - run: uv venv
          - run: uv pip install -e ".[dev]"
          - run: uv run ruff check .
          - run: uv run mypy src
          - run: uv run pytest -q

**What each part does:**

YAML nests by indentation, so the spaces matter: two per level, never tabs.

- `name: ci` is the label shown in GitHub's Actions tab and on the status badge.
- `on: [push, pull_request]` runs the workflow on every push to any branch and on every
  pull request.
- `jobs:` holds one job, called `check`. A job is a list of steps run in order on one
  machine; if any step fails, the job stops and goes red.
- `runs-on: ubuntu-latest` asks for a fresh Linux virtual machine each time, so nothing
  from your laptop leaks in.
- `uses: actions/checkout@v7` runs a published action that clones your repository onto
  that machine. `@v7` pins the action's major version, the latest as of October 2026.
- `uses: astral-sh/setup-uv@v10.2.0` installs `uv` on the machine, again pinned to the current
  major version. Check both actions' release pages before copying this file later.
- `run: uv venv` and `run: uv pip install -e ".[dev]"` are exactly Step 5, repeated on the
  clean machine. If they fail there, your `pyproject.toml` depends on something your
  laptop happens to have.
- `run: uv run ruff check .` lints every file. `uv run` runs a command inside the project's
  environment.
- `run: uv run mypy src` type-checks the package (not the tests, which keeps test code
  free to be loose).
- `run: uv run pytest -q` runs the tests; `-q` (quiet) prints one dot per passing test
  instead of a line each.

A green badge from commit one is a small thing that says a lot.

**Check it:** nothing runs this file locally; GitHub runs it the first time you push your
copy there (Step 12a). Locally, Step 11 runs the same three checks CI runs. You can catch
indentation mistakes now with `cat .github/workflows/ci.yml`: every `- ` line under `steps:`
must start in the same column.

## Step 10 — Write one real test

**Where:** `tests/test_package.py` — new file.
**Why this file exists:** not a placeholder. It proves the package installs, imports, and
exposes a version in the right shape, which is the contract every later tool relies on.

**Add this code:**

    from cartographer import __version__

    def test_package_exposes_a_version() -> None:
        assert isinstance(__version__, str)
        assert __version__.count(".") == 2

**What each part does:**

- `from cartographer import __version__` imports one name from the package. If the package
  is not installed, or does not define `__version__`, the test fails here, at import.
- The two blank lines after the import are Python's standard spacing before a top-level
  function; ruff checks it.
- `def test_package_exposes_a_version() -> None:` — pytest collects any function whose name
  starts with `test_` in any file whose name starts with `test_`. The name says what is
  being promised, so a failure reads as a sentence. `-> None` is the return-type hint; a
  test returns nothing.
- `assert isinstance(__version__, str)` checks the version is text, not a number or a
  tuple.
- `assert __version__.count(".") == 2` checks it has three parts, `major.minor.patch`.

## Step 11 — Give the package its version, and run the test

**Where:** `src/cartographer/__init__.py` — edit to the empty file from Step 3.
**Why this change exists:** the test from Step 10 imports `__version__`, so the package has
to define it.

Open the file (it is empty) and make this its only line:

**Add this code:**

    __version__ = "0.0.1"

**What each part does:** `__version__` is the conventional name for a package's version
string; the double underscores mark it as a name tools look for, not one you invented. The
value matches `version` in `pyproject.toml`. It is a plain string so nothing has to be
computed at import time.

**Check it:** confirm it passes locally before committing, then run the lint and type
checks too:

    uv run pytest -q
    uv run ruff check .
    uv run mypy src

You should see `1 passed`, then `All checks passed!` from ruff and
`Success: no issues found` from mypy. These are the three checks you will run at the end of
every day. `ModuleNotFoundError` means Step 5's install did not happen;
`ImportError: cannot import name '__version__'` means this file was not saved. `uv run` may
also create a `uv.lock` file the first time: that is uv recording the exact version of
every package it resolved. It is meant to be committed, and Step 12 will pick it up.

## Step 12 — Make the first commit

**Where:** the repo root.
**Why this step exists:** a commit is a saved snapshot in the history. This one is the
scaffold everything else builds on.

**Run this:**

    git add -A
    git commit -m "Day-00 | <your name> | Add. Project scaffold"
    git tag day-00

**What each part does:**

- `git add -A` stages every new, changed and deleted file in the repository, except what
  `.gitignore` excludes. **Staging** means "include this in the next commit".
- `git commit -m "..."` records the staged files as one commit with that message. Every
  commit in the series uses one format, `Day-NN | <your name> | <Action>. <message>`:
  `Day-00` says which day it belongs to; the name says who made it; the **action** is one
  plain verb — `Add`, `Update`, `Refactor`, `Delete` or `Fix` — followed by a full stop;
  and the message says briefly what changed. Today only adds new files, so it is `Add`.
  Put your own name where the command shows a name.
- `git tag day-00` puts a **tag**, a permanent name, on the commit you just made. Every day
  ends with one, so `git diff day-00 day-01` later shows exactly what a day changed, and
  `git checkout day-00` takes you back to it. It is a lightweight local tag: just a name,
  with no message of its own.

**Check it:**

    git log --oneline

One line, `(HEAD -> main, tag: day-00) Day-00 | <your name> | Add. Project scaffold`. Then run `git show --stat HEAD` and confirm
`.venv` and `.env` are not in the file list.

## Step 12a — Optional: put your copy on GitHub and watch CI run

**Where:** GitHub in your browser, then the repo root in your terminal.
**Why this step exists:** the CI file from Step 9 only runs on GitHub. Pushing your own copy
to your own account is the only way to watch it run. Skip this step and nothing later breaks:
every day still works locally, and Step 11's three checks are the same ones CI runs.

On GitHub, create a new repository named `cartographer` on your own account. Leave it
**empty**: no README, licence or `.gitignore`, because your first commit already has what it
needs and extra files on GitHub would make the first push conflict. GitHub then shows the
repository's SSH address; it looks like the one below, with your username in it.

**Run this:**

    git remote add origin git@github.com:<your-github-username>/cartographer.git
    git push -u origin main

**What each part does:**

- `git remote add origin <url>` records the GitHub address of your repository under the
  conventional short name `origin`, so later commands can say `origin` instead of the full
  address. The URL is the SSH form, `git@github.com:<account>/<repo>.git`; replace
  `<your-github-username>` with your own. It needs an SSH key added to your GitHub account;
  if the push says `Permission denied (publickey)`, add one first (GitHub's documentation on
  SSH keys walks through it), or use the HTTPS address GitHub shows instead.
- `git push` sends your commits to `origin`. `-u` (set upstream) remembers that your local
  `main` tracks `origin/main`, so on later days a bare `git push` knows where to go.

**Check it:** open your repository on GitHub and click the **Actions** tab. A run of the `ci`
workflow appears within a few seconds of the push: a yellow dot while it runs, then a green
tick when lint, types and tests all pass, or a red cross if one failed. Click a red run, then
the failing step, to read its output; a failure at `uv pip install` usually means a typo in
`pyproject.toml`, and a failure at `pytest` usually means Step 11's file was not committed.
From now on, every `git push` of a day's work starts a new run.

## Step 14 — Clone the repository cartographer will study

**Where:** any terminal. Nothing in this step touches the cartographer repository.
**Why this step exists:** an agent that maps unfamiliar code needs unfamiliar code to map,
and the same code every day, or no two days' results can be compared. That code is
**the target**: `pallets/click`, the Python library behind many command-line tools. It is
written in the series' language, it is mid-sized so a full run fits a free-tier budget, and
it is the subject of every demo from here to the end. You clone it once, today, and every
later day uses this one copy.

**Run this:**

    mkdir -p ~/workspace/personal/targets
    git clone --branch 8.5.0 https://github.com/pallets/click ~/workspace/personal/targets/click
    git -C ~/workspace/personal/targets/click rev-parse HEAD     # must print 8b19813f2bfca99f1018a587a8cf54fc959f2e5d
    echo 'export CARTOGRAPHER_TARGET="$HOME/workspace/personal/targets/click"' >> ~/.zshrc
    source ~/.zshrc

**What each part does:**

- `mkdir -p ~/workspace/personal/targets` creates a folder for target repositories, next to
  `cartographer` rather than inside it. A clone inside your repository would show up in
  `git status` and could be committed by accident; outside it, that cannot happen. It is
  also not under `/tmp`, which macOS empties on reboot: a thirty-day series outlives many
  reboots.
- `git clone <url> <folder>` downloads the repository into that folder. `--branch 8.5.0`
  checks out the release tagged `8.5.0` instead of whatever the main branch holds today.
  That is the **pin**: click keeps changing, and if your copy changed between days, a map
  that got better or worse could be the code moving rather than your agent. Pinned, every
  file count, token count and score in the series is a number about the same code.
  There is deliberately no `--depth 1` here. Later in the series the agent asks which
  revision of click to map and offers the repository's other branches and tags as the
  choices, so the clone keeps the full history. The extra download happens once; every day still reads the pinned commit.
- `git -C <folder> rev-parse HEAD` prints the full commit id, the **SHA**, of what you
  checked out. `-C` runs git as if you were inside that folder. A tag is a name that could in
  principle be moved; the SHA cannot, so it is the value the series records. It must be
  `8b19813f2bfca99f1018a587a8cf54fc959f2e5d`. (The text after `#` is a comment for you;
  the shell ignores it.)
- `echo '...' >> ~/.zshrc` appends one line to your shell's startup file, so every new
  terminal sets `CARTOGRAPHER_TARGET` to the clone's path. The single quotes keep `$HOME`
  unexpanded until the shell reads the file, and `>>` appends where `>` would overwrite the
  whole file. If your shell is bash, write to `~/.bashrc` instead, here and in the next line.
  This is safe to put in a file because a path is not a secret. Tomorrow's API key is the
  opposite: it is loaded into the terminal and never written to any file.
- `source ~/.zshrc` re-reads the startup file in this terminal, so the variable exists now
  rather than only in terminals you open later.

From here on, every command in the series refers to the target as `"$CARTOGRAPHER_TARGET"`,
always in double quotes, never as a literal path. The quotes keep the path in one piece if
it ever contains a space.

**Check it:**

    echo "$CARTOGRAPHER_TARGET"
    git -C "$CARTOGRAPHER_TARGET" rev-parse HEAD

The first line prints the full path, ending in `/workspace/personal/targets/click`. The
second prints `8b19813f2bfca99f1018a587a8cf54fc959f2e5d`. These two lines open every later
day as its readiness check.

- An empty first line means the variable is not set in this terminal: run
  `source ~/.zshrc`, or open a new terminal, and check that the `export` line is at the end
  of the file.
- `fatal: Remote branch 8.5.0 not found` means a typo in the tag.
- `fatal: destination path ... already exists` means you cloned before; run the
  `rev-parse` line to see what you have.
- If `rev-parse` prints any other SHA, the folder holds a different version of click. Do
  not work around it, because every later number would be about different code. Delete the
  folder with `rm -rf ~/workspace/personal/targets/click` and run the `git clone` line
  again.

## Check before you call it done

    git log --oneline          # one commit, tagged day-00, and it is yours
    git config user.email      # personal address
    echo "$CARTOGRAPHER_TARGET"                    # the target's path
    git -C "$CARTOGRAPHER_TARGET" rev-parse HEAD   # 8b19813f2bfca99f1018a587a8cf54fc959f2e5d

What each confirms: `git log --oneline` shows the history one commit per line, and it
should be exactly the scaffold commit, with the `day-00` tag on it. `git config user.email`
reads back the identity from Step 2. The last two are Step 14's check: the target exists,
the variable points at it, and it is pinned to the right commit.
