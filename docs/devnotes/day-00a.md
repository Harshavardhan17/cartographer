# Primer: Six ideas that explain every AI agent, before any code

Dev notes for this day's post: [read the post](https://harshakatkam.dev/agents-from-zero).
Step numbers follow the full build guide; steps only the repository owner needs, such as publishing to GitHub, are left out. New here? Start with [how to use these notes](README.md).

---

**Today's build:** nothing to build, two things to check

No code today. The primer is reading, plus a few optional experiments you paste into a
terminal, and Day 01 is where the first line of the agent gets written. This page makes sure
that when you open Day 01, nothing stops you in the first ten minutes, and gives you a way to
check the six ideas actually landed.

Time: about 15 minutes, after reading the post.

## Commands and tools today

| Command | What it does |
|---|---|
| `echo "$CARTOGRAPHER_TARGET"` | Prints the path of the target repository Day 00 cloned; empty means your shell profile is not loaded |
| `git -C "$CARTOGRAPHER_TARGET" rev-parse HEAD` | Prints the target's commit, which must be `8b19813f2bfca99f1018a587a8cf54fc959f2e5d` |
| `python3 --version` | Prints your Python version, which must be 3.12 or later |
| `uv --version` | Prints uv's version, proving it is installed |

New tools today: none

## 1. Be ready for Day 01

Day 00 did the setup and Day 01 loads your key, so do not duplicate either here. Just confirm
you can tick these:

- [ ] You completed Day 00, so `~/workspace/personal/cartographer` exists with its first commit.
- [ ] The target Day 00 cloned is in place. These two lines are the readiness check that
      opens every day from here on:

          echo "$CARTOGRAPHER_TARGET"                    # ends in /workspace/personal/targets/click
          git -C "$CARTOGRAPHER_TARGET" rev-parse HEAD   # 8b19813f2bfca99f1018a587a8cf54fc959f2e5d

      An empty first line or a different SHA means Day 00's Step 14 needs redoing.
- [ ] `python3 --version` prints 3.12 or later, and `uv --version` prints something.
- [ ] You have an OpenRouter account. If you ran the post's experiments you already created a
      key; if not, Day 01 shows how to load one into your shell without ever writing it to a
      file. Either way, no key goes in any file.

If any box is empty, fix that before Day 01 rather than during it.

## 2. Check the six ideas landed

These are the same nine questions as the quiz at the end of the post. Answer each in one
sentence, out loud or on paper, before looking at the answers. If one will not come, reread
the idea named after it.

1. A model confidently describes a function that does not exist. Why is that possible, and
   what reduces it? (Idea 1)
2. Your question is twelve words long. Will `prompt_tokens` be 12? (Idea 2)
3. A toy window holds 100 tokens. Your instructions are 15, a file is 70 and your question is
   10. How much room is left for the reply, and what happens if it needs more? (Idea 3)
4. Turn two of a chat clearly "remembers" turn one. Where does that memory live? (Idea 4)
5. Every question is 10 tokens and every answer 20. How many input tokens does turn three
   send? (Idea 4)
6. An agent "read a file". Who opened it? (Idea 5)
7. What is in a tool call's `arguments` field, and why should your code check it? (Idea 5)
8. What stops an agent loop from running forever, and who owns it? (Idea 6)
9. What one question separates a chatbot, a workflow and an agent?

**Answers.**

1. The model produces likely text, not checked text. Giving it the real source to answer
   from (grounding) reduces it; no prompt removes it entirely.
2. Almost certainly not. Tokens are not words, and the provider also counts the formatting
   around your message. The real number is in the response's `usage` block.
3. 5 tokens. The reply is cut off and `finish_reason` is `length`. Sending less fixes it; a
   better prompt does not.
4. In your program's list of messages, which it resends with every request.
5. 70: two questions, two answers and the new question.
6. Your code. The model returned a tool call, and your code ran the function and sent back
   the result.
7. A string of JSON the model wrote. It can be malformed, name a file that does not exist,
   or ask for a tool you never described.
8. A limit in your code, such as a maximum number of turns. The model never stops the loop
   itself.
9. Who decides the next step: you every turn, your code in advance, or the model inside a
   loop you bound.

When all nine come easily, you are ready. Tomorrow every one of them becomes code.

## No git step today

Nothing changed in the repository, so there is nothing to commit. Day 01 opens the first
feature branch.
