"""Builds Sensei's system prompt and turns slash commands into instructions.

The system prompt has two blocks:
1. a *stable* block (persona + all knowledge maps) that rarely changes and is prompt-cached;
2. a *session* block (date, profile, settings, recent log, due reviews) built once per session.

Slash-command instructions are read from ``.claude/commands/*.md`` so Claude Code and the
app always behave the same way.
"""

from __future__ import annotations

import re

from . import journal as j

APP_NOTE = """\
## Running inside the Sensei app

You are running inside the standalone Sensei app, not Claude Code. You cannot read or edit
files yourself: the persona, knowledge maps, profile, settings, recent learning log and due
review items are already included below, and the app saves the journal when the user runs
/wrap. When command instructions mention reading or updating files, use the information
provided here instead and skip any file-editing or git steps.
"""


def stable_block() -> str:
    parts = [j.read(j.PROMPTS / "persona.md"), APP_NOTE, "# Knowledge maps\n"]
    for domain in j.KNOWLEDGE_DOMAINS:
        text = j.read(j.KNOWLEDGE / f"{domain}.md")
        if text:
            parts.append(f'<knowledge_map domain="{domain}">\n{text.strip()}\n</knowledge_map>')
    return "\n\n".join(parts)


def describe_settings(settings: dict) -> str:
    return (
        f"- language: {settings['language']} (auto = mirror the user)\n"
        f"- depth: {settings['depth']} / 5\n"
        f"- style: {settings['style']}\n"
        f"- turn length: {settings['turn_length']}"
    )


def session_block(settings: dict) -> str:
    due = j.due_reviews()
    due_md = "\n".join(f"- {i.idea} ({i.domain}, learned {i.learned})" for i in due) or "(none due)"
    log = j.recent_log() or "(no previous sessions yet — this is the first one!)"
    library = ", ".join(j.library_files()) or "(empty)"
    return f"""# Session context

Today's date: {j.today().isoformat()} ({j.today().strftime('%A')})

## Learner settings
{describe_settings(settings)}

## Learner profile
{j.read(j.PROFILE).strip()}

## Recent learning log (newest first)
{log}

## Review items due today
{due_md}

## Documents in the user's library
{library}
"""


def system_blocks(settings: dict) -> list[dict]:
    return [
        {"type": "text", "text": stable_block(), "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": session_block(settings)},
    ]


# --------------------------------------------------------------------------- commands

PROMPT_COMMANDS = ["daily", "talk", "dive", "surprise", "connect", "quiz"]


def command_body(name: str, args: str) -> str:
    """The body of .claude/commands/<name>.md (frontmatter stripped, $ARGUMENTS filled in)."""
    text = j.read(j.COMMANDS / f"{name}.md")
    body = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S).strip()
    return body.replace("$ARGUMENTS", args or "(none)")


def command_instructions(name: str, args: str) -> str | None:
    """Return the instruction text for a prompt-based slash command, or None if unknown."""
    if name not in PROMPT_COMMANDS:
        return None
    body = command_body(name, args)
    return f"[Command /{name}]\n\n{body}" if body else None


def export_prompt(settings: dict) -> str:
    """One self-contained prompt for claude.ai Projects, LibreChat agents, etc."""
    note = (
        "## Running in a chat app\n\nYou cannot edit files. When the user says \"wrap up\" "
        "(or /wrap), give a recap formatted as a learning-log entry they can paste into "
        "journal/log.md:\n\n### YYYY-MM-DD — <main topic>\n- **Domains:** ...\n- **Key ideas:** ...\n"
        "- **Connections made:** A ↔ B\n- **User's thoughts / opinions:** ...\n- **Open threads (next time):** ...\n"
    )
    stable = stable_block().replace(APP_NOTE, note)
    return stable + "\n\n" + session_block(settings)
