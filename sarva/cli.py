"""Terminal chat with Sarva."""

from __future__ import annotations

from .core import Sarva

BANNER = """\
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  物知りの友 · The All-Knowing — Sarva
  /daily  /talk <topic>  /surprise  /help  /wrap
  (exit with /wrap to save, or Ctrl+D to quit without saving)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""


def main(start: str | None = None, commit: bool = False) -> None:
    sarva = Sarva()
    print(BANNER)
    pending = start
    while True:
        if pending is None:
            try:
                pending = input("\nあなた / You › ")
            except (EOFError, KeyboardInterrupt):
                print("\nまたね！ (not saved — use /wrap next time to keep a log)")
                return
        text, pending = pending.strip(), None
        if not text:
            continue
        if text.lower() in ("/wrap", "/exit", "/quit", "/bye"):
            print("\nSarva › ", end="", flush=True)
            print(sarva.wrap(commit=commit))
            return
        print("\nSarva › ", end="", flush=True)
        for chunk in sarva.handle(text):
            print(chunk, end="", flush=True)
        print()
