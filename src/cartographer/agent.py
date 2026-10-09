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
