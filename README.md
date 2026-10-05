# cartographer

An agent that reads a codebase you have never seen and produces an onboarding map:
the entry points, the small fraction of the code that carries the weight, how data
moves through it, and where your first change would go.

Built in the open over 30 days. Each day adds one capability and one write-up.

## Status

Day 0. Nothing works yet. Follow along or come back at v1.0.

## Why

Every developer has been dropped into an unfamiliar repository and spent a week
finding the front door. The information needed to shortcut that is all in the repo
already; it is just not in a shape a newcomer can read.

## Quickstart

Not yet. This section fills in on Day 07.

## Limitations

Tracked honestly as they are found, starting Day 07.

## Dev notes

`docs/devnotes/` holds one file per day of the build, for anyone who wants to build
cartographer themselves rather than only read about it. Each day's file lists the files
you will touch, a table of every command you run and what it does, then numbered steps:
the code to type, an explanation of every line, and a check that tells you it worked.

How to use them:

1. Start at `docs/devnotes/day-00.md` and go in order, because each day starts from the
   previous day's code. `docs/devnotes/day-00a.md` is a short no-code primer on how
   agents work; read it whenever you like.
2. Run every command from the repository root unless a step says otherwise.
3. Finish each day with its tests, lint and type checks passing, and a local `day-NN`
   tag, so you can always return to or diff against a finished day.
4. `docs/devnotes/TOOLS.md` explains each tool the notes use, from git to pytest.
5. Step numbers sometimes skip. The missing steps only maintain this public repository;
   nothing you need to build or run the agent is left out.

## Licence

MIT
