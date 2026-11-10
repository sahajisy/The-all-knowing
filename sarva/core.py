"""The conversation engine shared by the terminal and web interfaces."""

from __future__ import annotations

import base64
import subprocess
from collections.abc import Iterator
from typing import Literal

import anthropic
from pydantic import BaseModel, Field

from . import journal as j
from . import prompt

BETAS = ["server-side-fallback-2026-07-01"]
WEB_SEARCH_TOOL = {"type": "web_search_20260209", "name": "web_search", "max_uses": 3}
MAX_DOC_BYTES = 20 * 1024 * 1024

HELP = """\
**Commands / コマンド**

| Command | |
|---|---|
| `/daily` | Today's topic / 今日の話題 |
| `/talk <topic>` | Talk about anything |
| `/dive <topic>` | Deeper guided exploration |
| `/surprise` | A surprising fact from any field |
| `/connect <A> <B>` | Hidden links between two things |
| `/quiz` | Review what you learned before |
| `/read <file>` | Discuss a document from `library/` |
| `/lang ja\\|en\\|mix\\|auto` | Switch language |
| `/settings [key value]` | depth 1-5 · style · turn_length · web_search on/off · effort |
| `/wrap` | Recap and save today's session to your journal |
| `/help` | This list |

Or just start talking. / 普通に話しかけてもOKです。
"""


class LogEntry(BaseModel):
    main_topic: str = Field(description="Short title of the session's main topic")
    domains: list[str]
    key_ideas: list[str] = Field(description="3-5 key ideas discussed")
    connections: list[str] = Field(description="Cross-domain connections made, formatted 'A ↔ B'")
    user_thoughts: list[str] = Field(description="The user's own opinions/experiences shared")
    open_threads: list[str] = Field(description="Things to explore next time")


class ReviewIdea(BaseModel):
    idea: str = Field(description="One fact or idea phrased as a short review prompt/answer pair")
    domain: str


class ReviewResult(BaseModel):
    idea: str = Field(description="Exact text of a review item that was quizzed this session")
    remembered: bool


class KnowledgeEntry(BaseModel):
    domain: Literal[
        "technology", "japan", "science", "history", "philosophy", "economics-business",
        "arts-culture", "world-geography", "health-lifestyle", "language", "connections",
    ]
    line: str = Field(description="One-line entry: '- **Name / 日本語** — hook → links'")


class WrapUp(BaseModel):
    recap: str = Field(description="Friendly recap for the user in the session's language (markdown)")
    log: LogEntry
    new_review_items: list[ReviewIdea] = Field(description="2-4 most important ideas to review later")
    review_results: list[ReviewResult] = Field(description="Results for review items quizzed this session, if any")
    profile_notes: list[str] = Field(description="New facts learned about the user (not already in profile)")
    knowledge_entries: list[KnowledgeEntry] = Field(description="Great new concepts/connections worth adding to the maps (0-3)")


WRAP_INSTRUCTION = """[Command /wrap]

The session is ending. Produce the wrap-up: a short friendly recap for the user (3-5 key
things we talked about, one connection, one question to think about until next time, and a
warm goodbye), plus the journal updates. Only include profile notes and knowledge entries
that are genuinely new and accurate. For review results, use the exact idea text from the
review items list. If we barely talked, keep everything minimal."""


class Sarva:
    def __init__(self, client: anthropic.Anthropic | None = None):
        self.client = client or anthropic.Anthropic()
        self.settings = j.load_settings()
        self.system = prompt.system_blocks(self.settings)
        self.messages: list[dict] = []
        self.pending_notes: list[str] = []  # setting changes announced with the next user turn

    # ------------------------------------------------------------------ public API

    def handle(self, text: str) -> Iterator[str]:
        """Process one user input (message or slash command) and yield reply text chunks."""
        text = text.strip()
        if not text:
            return
        if text.startswith("/"):
            name, _, args = text[1:].partition(" ")
            name, args = name.lower(), args.strip()
            if name == "help":
                yield HELP
                return
            if name in ("lang", "settings"):
                yield self._settings_command(name, args)
                return
            if name == "wrap":
                yield self.wrap()
                return
            if name == "read":
                yield from self._read_command(args)
                return
            instructions = prompt.command_instructions(name, args)
            if instructions is None:
                yield f"Unknown command `/{name}`. Type `/help` for the list."
                return
            yield from self._turn(instructions)
            return
        yield from self._turn(text)

    def wrap(self, commit: bool = False) -> str:
        if not any(m["role"] == "assistant" for m in self.messages):
            return "We haven't talked yet today — nothing to save. またね！"
        messages = self.messages + [{"role": "user", "content": WRAP_INSTRUCTION}]
        response = self.client.beta.messages.parse(
            model=self.settings["model"],
            max_tokens=16000,
            system=self.system,
            messages=messages,
            output_format=WrapUp,
            output_config={"effort": self.settings["effort"]},
            betas=BETAS,
            fallbacks="default",
        )
        if response.stop_reason == "refusal" or response.parsed_output is None:
            return "Sorry — I couldn't produce the wrap-up this time. Your conversation is still here; try `/wrap` again."
        result: WrapUp = response.parsed_output
        self._save(result)
        saved = "\n\n_Saved to journal/ (log, review queue, profile"
        saved += ", knowledge maps)._" if result.knowledge_entries else ")._"
        if commit:
            saved += "\n\n" + commit_journal(result.log.main_topic)
        self.messages = []
        return result.recap + saved

    # ------------------------------------------------------------------ internals

    def _turn(self, user_content) -> Iterator[str]:
        """Send a user turn and stream the reply, continuing paused server-tool turns."""
        self.messages.append({"role": "user", "content": user_content})
        start = len(self.messages) - 1
        if self.pending_notes:
            # Mid-conversation system message: tells Sarva about setting changes
            # without editing the cached system prompt.
            note = (f"The user changed learner settings: {', '.join(self.pending_notes)}. "
                    f"Apply them from this reply on.\nCurrent settings:\n{prompt.describe_settings(self.settings)}")
            self.messages.append({"role": "system", "content": note})
            self.pending_notes = []
        tools = [WEB_SEARCH_TOOL] if self.settings["web_search"] else []
        try:
            while True:
                kwargs = {"tools": tools} if tools else {}
                with self.client.beta.messages.stream(
                    model=self.settings["model"],
                    max_tokens=16000,
                    system=self.system,
                    messages=self.messages,
                    thinking={"type": "adaptive"},
                    output_config={"effort": self.settings["effort"]},
                    cache_control={"type": "ephemeral"},
                    betas=BETAS,
                    fallbacks="default",
                    **kwargs,
                ) as stream:
                    for event in stream:
                        if event.type == "text":
                            yield event.text
                    message = stream.get_final_message()
                if message.stop_reason == "refusal":
                    del self.messages[start:]
                    yield "\n\n_(I can't continue with that one — let's try a different angle.)_"
                    return
                self.messages.append({"role": "assistant", "content": message.content})
                if message.stop_reason == "pause_turn":
                    continue  # web search still running: let the server resume the turn
                if message.stop_reason == "max_tokens":
                    yield "\n\n_(…I got cut off. Say 「続けて」 / “continue” and I'll go on.)_"
                return
        except anthropic.AuthenticationError:
            del self.messages[start:]
            yield "⚠️ No valid Anthropic API key. Set ANTHROPIC_API_KEY (see README)."
        except anthropic.RateLimitError:
            del self.messages[start:]
            yield "⚠️ Rate limited — wait a minute and try again."
        except anthropic.APIStatusError as e:
            del self.messages[start:]
            yield f"⚠️ API error ({e.status_code}): {e.message}"
        except anthropic.APIConnectionError:
            del self.messages[start:]
            yield "⚠️ Network error — check your internet connection."

    def _settings_command(self, name: str, args: str) -> str:
        if name == "lang":
            key, raw = "language", args
        elif not args:
            rows = "\n".join(f"| {k} | `{v}` | {', '.join(map(str, j.SETTING_CHOICES.get(k, ['claude-…'])))} |"
                             for k, v in self.settings.items())
            return f"| Setting | Current | Options |\n|---|---|---|\n{rows}\n\nChange with `/settings <key> <value>`, e.g. `/settings depth 5`."
        else:
            key, _, raw = args.partition(" ")
        try:
            value = j.parse_setting(key.strip(), raw.strip())
        except ValueError as e:
            return f"⚠️ {e}"
        self.settings[key] = value
        j.save_settings(self.settings)
        if key in ("language", "depth", "style", "turn_length"):
            self.pending_notes.append(f"{key} = {value}")
        return f"✓ {key} = {value}"

    def _read_command(self, args: str) -> Iterator[str]:
        files = j.library_files()
        if not args:
            listing = "\n".join(f"- `{f}`" for f in files) or "(empty — put .md, .txt or .pdf files in library/)"
            yield f"**library/**\n\n{listing}\n\nUse `/read <file>`."
            return
        path = (j.LIBRARY / args).resolve()
        if path.parent != j.LIBRARY.resolve() or path.name not in files:
            yield f"Couldn't find `{args}` in library/. Available: {', '.join(files) or '(none)'}"
            return
        if path.stat().st_size > MAX_DOC_BYTES:
            yield "That file is too large (over 20 MB)."
            return
        instructions = prompt.command_body("read", path.name)
        instructions += "\n\nThe document is attached above; you don't need to find it in library/."
        if path.suffix.lower() == ".pdf":
            doc = {"type": "document", "title": path.name, "source": {
                "type": "base64", "media_type": "application/pdf",
                "data": base64.standard_b64encode(path.read_bytes()).decode()}}
        else:
            doc = {"type": "document", "title": path.name, "source": {
                "type": "text", "media_type": "text/plain", "data": path.read_text(encoding="utf-8", errors="replace")}}
        yield from self._turn([doc, {"type": "text", "text": "[Command /read]\n" + instructions.strip()}])

    def _save(self, w: WrapUp) -> None:
        log = w.log
        entry = "\n".join([
            f"### {j.today().isoformat()} — {log.main_topic}",
            f"- **Domains:** {' / '.join(log.domains)}",
            "- **Key ideas:**", *[f"  - {i}" for i in log.key_ideas],
            f"- **Connections made:** {'; '.join(log.connections) or '—'}",
            f"- **User's thoughts / opinions:** {'; '.join(log.user_thoughts) or '—'}",
            f"- **Open threads (next time):** {'; '.join(log.open_threads) or '—'}",
        ])
        j.add_log_entry(entry)
        j.record_reviews([(r.idea, r.remembered) for r in w.review_results])
        j.add_review_items([(r.idea, r.domain) for r in w.new_review_items])
        j.add_profile_notes(w.profile_notes, log.open_threads)
        j.add_knowledge_entries([(k.domain, k.line) for k in w.knowledge_entries])


def commit_journal(topic: str) -> str:
    """Commit (and try to push) the journal so memory survives across machines/sessions."""
    def git(*args):
        return subprocess.run(["git", *args], cwd=j.ROOT, capture_output=True, text=True, timeout=60)

    if git("rev-parse", "--is-inside-work-tree").returncode != 0:
        return "_(Not a git repository — skipped commit.)_"
    git("add", "journal", "knowledge")
    c = git("commit", "-m", f"Learning log: {j.today().isoformat()} — {topic}")
    if c.returncode != 0:
        return "_(Nothing new to commit.)_"
    p = git("push")
    return "_Committed and pushed to git._" if p.returncode == 0 else "_Committed locally (push failed — run `git push` later)._"
