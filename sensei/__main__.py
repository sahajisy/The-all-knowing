"""Entry point: ``python -m sensei [chat|web|export]``."""

from __future__ import annotations

import argparse

from . import journal, prompt


def main() -> None:
    parser = argparse.ArgumentParser(prog="sensei", description="物知りの友 — The All-Knowing learning companion")
    sub = parser.add_subparsers(dest="cmd")

    chat = sub.add_parser("chat", help="chat in the terminal (default)")
    chat.add_argument("first", nargs="*", help="optional first message, e.g. /daily")
    chat.add_argument("--commit", action="store_true", help="git commit + push the journal after /wrap")

    web = sub.add_parser("web", help="open a chat page in your browser")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8765)
    web.add_argument("--commit", action="store_true", help="git commit + push the journal after /wrap")

    export = sub.add_parser("export", help="write one prompt file for claude.ai Projects / LibreChat")
    export.add_argument("--out", default="dist/sensei-prompt.md")

    args = parser.parse_args()
    if args.cmd == "web":
        from . import web as web_mod
        web_mod.main(args.host, args.port, args.commit)
    elif args.cmd == "export":
        out = journal.ROOT / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(prompt.export_prompt(journal.load_settings()), encoding="utf-8")
        print(f"Wrote {out.relative_to(journal.ROOT)} ({out.stat().st_size // 1024} KB)")
    else:
        from . import cli
        first = " ".join(getattr(args, "first", []) or []) or None
        cli.main(first, getattr(args, "commit", False))


if __name__ == "__main__":
    main()
