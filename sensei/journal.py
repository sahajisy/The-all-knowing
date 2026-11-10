"""Sensei's memory: the learner profile, settings, session log, and review queue.

Everything lives in plain Markdown/JSON under ``journal/`` so the same memory is shared
by the app, Claude Code, and the user (who can read and edit it by hand).
"""

from __future__ import annotations

import datetime as dt
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOURNAL = ROOT / "journal"
KNOWLEDGE = ROOT / "knowledge"
LIBRARY = ROOT / "library"
PROMPTS = ROOT / "prompts"
COMMANDS = ROOT / ".claude" / "commands"

PROFILE = JOURNAL / "profile.md"
SETTINGS = JOURNAL / "settings.json"
LOG = JOURNAL / "log.md"
REVIEW = JOURNAL / "review.md"

DEFAULT_SETTINGS = {
    "language": "auto",
    "depth": 3,
    "style": "balanced",
    "turn_length": "medium",
    "web_search": False,
    "effort": "medium",
    "model": "claude-opus-5-5",
}

SETTING_CHOICES = {
    "language": ["auto", "ja", "en", "mix"],
    "depth": [1, 2, 3, 4, 5],
    "style": ["balanced", "socratic", "storyteller", "debate", "quick-facts"],
    "turn_length": ["short", "medium", "long"],
    "web_search": [True, False],
    "effort": ["low", "medium", "high", "xhigh", "max"],
}

REVIEW_INTERVALS = [1, 3, 7, 14, 30, 60, 120]


def today() -> dt.date:
    return dt.date.today()


# --------------------------------------------------------------------------- settings


def load_settings() -> dict:
    settings = dict(DEFAULT_SETTINGS)
    try:
        settings.update(json.loads(SETTINGS.read_text(encoding="utf-8")))
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return settings


def save_settings(settings: dict) -> None:
    SETTINGS.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_setting(key: str, raw: str):
    """Validate a ``/settings key value`` pair. Returns the typed value or raises ValueError."""
    if key == "model":
        if not raw.startswith("claude-"):
            raise ValueError("model must be a Claude model id, e.g. claude-opus-5-5")
        return raw
    if key not in SETTING_CHOICES:
        raise ValueError(f"unknown setting '{key}'. Options: {', '.join([*SETTING_CHOICES, 'model'])}")
    choices = SETTING_CHOICES[key]
    if key == "depth":
        value = int(raw) if raw.isdigit() else None
    elif key == "web_search":
        value = {"on": True, "true": True, "yes": True, "off": False, "false": False, "no": False}.get(raw.lower())
    else:
        value = raw.lower()
    if value not in choices:
        raise ValueError(f"{key} must be one of: {', '.join(map(str, choices))}")
    return value


# --------------------------------------------------------------------------- reading


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def recent_log(n: int = 5) -> str:
    """The newest ``n`` session entries from the log (entries start with '### ')."""
    text = read(LOG)
    _, _, sessions = text.partition("## Sessions")
    entries = re.split(r"(?m)^(?=### )", sessions)
    entries = [e.strip() for e in entries if e.strip().startswith("### ")]
    return "\n\n".join(entries[:n])


@dataclass
class ReviewItem:
    idea: str
    domain: str
    learned: str
    interval: int
    next_review: str

    def row(self) -> str:
        cells = [self.idea.replace("|", "/"), self.domain, self.learned, str(self.interval), self.next_review]
        return "| " + " | ".join(cells) + " |"


def load_review() -> list[ReviewItem]:
    items = []
    for line in read(REVIEW).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 5 or cells[0] in ("Idea", "") or set(cells[0]) <= {"-"}:
            continue
        try:
            items.append(ReviewItem(cells[0], cells[1], cells[2], int(cells[3]), cells[4]))
        except ValueError:
            continue
    return items


def save_review(items: list[ReviewItem]) -> None:
    text = read(REVIEW)
    head, sep, _ = text.partition("|---|")
    if not sep:
        head = "| Idea | Domain | Learned | Interval (days) | Next review |\n"
        sep = "|---|"
    header_end = "---|---|---|---|\n"
    body = "\n".join(i.row() for i in items)
    REVIEW.write_text(head + sep + header_end + body + ("\n" if body else ""), encoding="utf-8")


def due_reviews(limit: int = 8) -> list[ReviewItem]:
    now = today().isoformat()
    due = [i for i in load_review() if i.next_review <= now]
    return sorted(due, key=lambda i: i.next_review)[:limit]


def library_files() -> list[str]:
    if not LIBRARY.exists():
        return []
    return sorted(
        p.name for p in LIBRARY.iterdir()
        if p.is_file() and p.suffix.lower() in {".md", ".txt", ".pdf"} and p.name != "README.md"
    )


# --------------------------------------------------------------------------- writing


def _insert_after_heading(path: Path, heading: str, lines: list[str], newest_first: bool = False) -> None:
    """Add lines under a '## heading' section (after any HTML comment placeholder)."""
    if not lines:
        return
    text = read(path)
    block = "\n".join(lines)
    idx = text.find(heading)
    if idx == -1:
        text = text.rstrip() + f"\n\n{heading}\n\n{block}\n"
    else:
        start = text.find("\n", idx) + 1
        nxt = text.find("\n## ", start)
        end = len(text) if nxt == -1 else nxt + 1  # section body is text[start:end]
        section = text[start:end]
        # keep a placeholder comment (if any) at the top of the section
        m = re.match(r"\s*(<!--[^\n]*?-->[ \t]*\n)?", section)
        head, body = section[: m.end()], section[m.end():].strip("\n")
        head = head.strip("\n") + "\n" if head.strip() else ""
        if newest_first:
            body = block + ("\n\n" + body if body else "")
        else:
            body = (body + "\n" if body else "") + block
        trailer = "\n\n" if nxt != -1 else "\n"
        text = text[:start] + "\n" + head + body + trailer + text[end:]
    path.write_text(text, encoding="utf-8")


def add_log_entry(entry_md: str) -> None:
    _insert_after_heading(LOG, "## Sessions", [entry_md.strip()], newest_first=True)


def add_profile_notes(notes: list[str], open_threads: list[str]) -> None:
    existing = read(PROFILE)
    notes = [n for n in notes if n and n not in existing]
    threads = [t for t in open_threads if t and t not in existing]
    _insert_after_heading(PROFILE, "## Things Sensei has learned about the user", [f"- {n}" for n in notes])
    _insert_after_heading(PROFILE, "## Topics they want to explore later / いつか話したいこと", [f"- {t}" for t in threads])


def add_review_items(ideas: list[tuple[str, str]]) -> None:
    items = load_review()
    known = {i.idea for i in items}
    tomorrow = (today() + dt.timedelta(days=1)).isoformat()
    for idea, domain in ideas:
        if idea and idea not in known:
            items.append(ReviewItem(idea, domain, today().isoformat(), 1, tomorrow))
    save_review(items)


def record_reviews(results: list[tuple[str, bool]]) -> None:
    """Spaced repetition: remembered → next longer interval; forgotten → back to 1 day."""
    items = load_review()
    by_idea = {i.idea: i for i in items}
    for idea, remembered in results:
        item = by_idea.get(idea)
        if not item:
            continue
        if remembered:
            longer = [d for d in REVIEW_INTERVALS if d > item.interval]
            item.interval = longer[0] if longer else item.interval * 2
        else:
            item.interval = 1
        item.next_review = (today() + dt.timedelta(days=item.interval)).isoformat()
    save_review(items)


KNOWLEDGE_DOMAINS = [
    "technology", "japan", "science", "history", "philosophy", "economics-business",
    "arts-culture", "world-geography", "health-lifestyle", "language", "connections",
]


def add_knowledge_entries(entries: list[tuple[str, str]]) -> None:
    """Append one-line entries ('domain', '- **Name** — hook') to the knowledge maps."""
    for domain, line in entries:
        path = KNOWLEDGE / f"{domain}.md"
        if domain not in KNOWLEDGE_DOMAINS or not path.exists() or not line.strip():
            continue
        line = line.strip()
        if not line.startswith("- "):
            line = "- " + line
        text = read(path)
        if line in text:
            continue
        heading = "## Added in conversation / 会話から追加"
        if heading not in text:
            text = text.rstrip() + f"\n\n{heading}\n"
        path.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8")
