# Dev notes

These are the build notes for the cartographer series: one file per day, with every file you
create, every line you type, and every command you run, each one explained. If you are here to
build the agent yourself rather than read about it, this folder is where you work from.

## How the notes relate to the posts

Each day of the series is a blog post and a dev-notes file, and they do different jobs.

- **The post** explains one idea: why it matters, the version that fails, and the fix. It shows
  the key code, but not all of it, so it stays a five-minute read.
- **The dev notes** are the complete build. Where a file goes, what to type into it, what each
  line does, the command that checks it, and what you should see when it works.

Read the post first for the why. Then open the day's notes and build.

## How to use them, day by day

1. **Read the post.** Each day's notes link back to it at the top.
2. **Open the day's notes.** Start at the top; every day assumes the previous day's code.
3. **Run the readiness check.** Every day opens with the same two lines:

       echo "$CARTOGRAPHER_TARGET"
       git -C "$CARTOGRAPHER_TARGET" rev-parse HEAD

   The first must print the path of your clone of click; the second must print
   `8b19813f2bfca99f1018a587a8cf54fc959f2e5d`. If either is wrong, fix it before anything else
   (Day 00, Step 14 sets it up). Every number in the series is about that exact code.
4. **Follow the steps in order.** Each step says where you are working, why the file or change
   exists, the code to add, what every part of it does, and how to check it.
5. **Use the "Commands and tools today" table.** Near the top of each day, it lists every command
   you will run that day with one line on what it does. A tool you are meeting for the first time
   links to [TOOLS.md](TOOLS.md), which explains it and its flags.
6. **Check your work.** Each step ends with **Check it**: run the command and compare what you
   see with what the notes describe, including what a likely failure looks like and what causes
   it. Lint, types and tests should all pass before you commit.
7. **Commit and tag.** The last step of each day commits to that day's branch, in the format
   Day 00 explains (`Day-NN | <your name> | <Action>. <message>`), and tags it `day-NN`, so you
   can always get back to a known-good point.

You need an OpenRouter API key from Day 01 on. The free models are enough for the whole series.
The key is loaded into your terminal each session and never written to any file; the notes show
how.

## Stuck? Use the day tags

The reference repository carries a tag for every day: `day-00`, `day-01`, and so on up to
`day-30`. Each tag is the exact code that day's notes describe. Clone it into a separate folder,
so it never mixes with your own work:

    git clone https://github.com/Harshavardhan17/cartographer ~/cartographer-reference
    cd ~/cartographer-reference

Then:

- `git checkout day-07` puts the exact code Day 07 describes in that folder. Open the file you are
  stuck on and compare it with yours.
- `git diff day-06 day-07` shows exactly what one day changed, file by file. This is often the
  fastest way to find the one line you missed.
- `git diff day-06 day-07 -- src/cartographer/agent.py` narrows that to one file.
- `git checkout main` takes you back to the latest code.

Comparing is better than copying. If you paste the whole file, you skip the part where you learn
why your version did not work.

## What is left out, and why

The notes are generated from the author's full build guide, and a few steps in that guide are
only for the person who owns the public repository: writing the front-page README and licence,
creating that GitHub repository, pushing to it, opening and merging pull requests, and tagging
releases. None of that changes how the agent works, so it is not here.

Step numbers follow the full guide, so you will sometimes see a gap, for example Step 6 followed
by Step 8. Nothing is missing that you need: every step that builds, runs or tests the agent is
included. That includes the CI workflow, `.github/workflows/ci.yml`: you write it on Day 00 like
any other file. It runs only once your copy is on GitHub, so Day 00's optional Step 12a shows
how to push your copy to your own account and watch it run in the **Actions** tab. Nothing else
in the series depends on that push; locally, the same lint, type and test commands are what CI
runs.

## Every day

| Day | Notes | Title |
|---|---|---|
| Day 00 | [day-00.md](day-00.md) | Learn AI agents by building one, in 30 days |
| Primer | [day-00a.md](day-00a.md) | Six ideas that explain every AI agent, before any code |
| Day 01 | coming | Why your first agent should be 40 lines, not a framework |
| Day 02 | coming | An LLM is a stateless function. Everything else is you |
| Day 03 | coming | Your repo does not fit in the context window. Now what? |
| Day 04 | coming | Stop parsing prose. Make the model return a struct |
| Day 05 | coming | Temperature, top-p, and the myth of creative settings |
| Day 06 | coming | Tool calling, hand-rolled: what the API actually sends |
| Day 07 | coming | I gave it a repo I had never seen. It found the front door |
| Day 08 | coming | Your tool descriptions are the prompt. Write them like a contract |
| Day 09 | coming | MCP went stateless and every tutorial you have read is now wrong |
| Day 10 | coming | Anatomy of an MCP server: tools, resources, prompts |
| Day 11 | coming | Build an MCP server you will actually keep using |
| Day 12 | coming | How an MCP server asks you a question now that it cannot call you |
| Day 13 | coming | The confused deputy living inside your agent |
| Day 14 | coming | My editor can now answer questions about a repo it has never indexed |
| Day 15 | coming | Chains break. Graphs do not. Why LangGraph exists |
| Day 16 | coming | State is the whole design. Everything else is plumbing |
| Day 17 | coming | The conditional edge that replaces your if-tree |
| Day 18 | coming | Cycles are the point: the thing chains cannot do |
| Day 19 | coming | How an agent survives a crash four thousand files in |
| Day 20 | coming | Interrupt, inspect, resume: keeping a human in the loop |
| Day 21 | coming | The whole explorer, rebuilt as a graph with an approval gate |
| Day 22 | coming | Memory is three different problems. Stop calling it one |
| Day 23 | coming | Retrieval is a tool the agent calls, not a stage it sits inside |
| Day 24 | coming | Multi-agent is usually a mistake. Here is when it is not |
| Day 25 | coming | Evals: how do you know your agent got worse? |
| Day 26 | coming | Observability: tracing a run you can actually debug |
| Day 27 | coming | Cost control: caching, routing, and cheap-model-first |
| Day 28 | coming | The seven ways agents fail in production |
| Day 29 | coming | The line I refuse to cross: it writes docs, never code |
| Day 30 | coming | 30 days, one agent, and the six things I would do differently |

## Tools

[TOOLS.md](TOOLS.md) explains every tool and command family the series uses: uv, python, pytest,
ruff, mypy, git, the shell, the MCP inspector, the claude command line, and the libraries the
project depends on, with what each flag does and the day it first appears.
