# The All-Knowing — 物知りの友

A daily **conversational learning companion** built on Claude. Instead of reading
Wikipedia pages, you *talk* with **Sarva** (सर्व), someone who seems to know everything.
You can talk in Japanese or English, and the conversation goes both ways, like one between
two people.

> **You:** 日本の暮らしについて話したい
>
> **Sarva:** いいですね！じゃあ「もったいない」から始めましょうか。実はこの言葉、ケニアの
> ノーベル平和賞受賞者ワンガリ・マータイさんが世界に広めたんです。そういえば、細胞にも
> 「もったいない」の仕組みがあって、大隅良典さんがノーベル賞を取ったオートファジーがまさに
> それなんですよ。…ちなみに、普段の生活で「もったいない」と感じるのはどんな時ですか？

## Three ways to use it (same Sarva, same memory)

| Where | Best for | Needs |
|---|---|---|
| **1. Claude Code** (claude.ai/code, desktop, terminal) | Easiest; memory saved to GitHub automatically | A Claude subscription |
| **2. Sarva app** (`python -m sarva web`) | A dedicated chat page on your computer or phone, with adjustable depth and style, your own documents, and optional web search | An Anthropic API key (pay per use) |
| **3. Claude app / LibreChat** (exported prompt) | Chatting on your phone in the Claude app, or in a self-hosted LibreChat | A Claude subscription, or LibreChat plus an API key |

All three read the same persona (`prompts/persona.md`), knowledge maps (`knowledge/`) and
journal (`journal/`).

---

### Voice conversation (Claude app)

To *talk* with Sarva out loud in the Claude app:

1. Create a **Project** called "Sarva".
2. Copy the whole of [`voice/CLAUDE.md`](voice/CLAUDE.md) into the Project's **custom instructions**.
3. Optional: upload `journal/profile.md` and `knowledge/connections.md` as Project knowledge.
4. Open a chat in the Project, tap the **voice** button, and say 「こんにちは、Sarva」.

Say "today's topic", "quiz me", "go deeper" or 「今日はここまで」 to wrap up, then "show the log" to get
a written entry for `journal/log.md`.

### 1. Claude Code

Open this repository in Claude Code and type a command, or just start talking:

| Command | 使い方 |
|---|---|
| `/daily` | 今日の話題: a fresh topic from a rotating domain, opened with a hook |
| `/talk <topic>` | Talk about anything: `/talk 日本の銭湯文化`, `/talk Kubernetes` |
| `/dive <topic>` | A deeper guided exploration: `/dive 量子コンピュータ` |
| `/surprise` | A random surprising fact, then discussion |
| `/connect <A> <B>` | Hidden links between two things: `/connect 寿司 blockchain` |
| `/quiz` | Friendly spaced-repetition review of past topics |
| `/read <file>` | Discuss a document you put in `library/` |
| `/settings [key value]` | Depth 1–5, style, turn length, language |
| `/lang ja\|en\|mix` | Switch language |
| `/wrap` | Recap and save the session to the journal (commits and pushes, so memory persists) |

### 2. The Sarva app

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...        # from console.anthropic.com

python -m sarva web                        # chat page → http://127.0.0.1:8765
python -m sarva                            # or chat in the terminal
python -m sarva chat /daily                # start straight into today's topic
python -m sarva web --commit               # also git commit + push the journal on /wrap
```

**On your phone (same Wi-Fi):** `SARVA_PASSWORD=choose-one python -m sarva web --host 0.0.0.0`,
then open `http://<your-computer's-IP>:8765` on the phone. The password is required because
anyone who can reach the page can spend your API credits.

The app supports the same commands as Claude Code (they're read from the same
`.claude/commands/` files), plus:

- **Learner settings** (`/settings`):
  `depth` 1–5 (curious beginner → expert peer) ·
  `style` balanced / socratic / storyteller / debate / quick-facts ·
  `turn_length` short / medium / long ·
  `language` auto / ja / en / mix ·
  `web_search` on/off (lets Sarva check recent facts) ·
  `effort` low / medium / high (thinking depth: higher is slower and costs more)
- **Your documents** (`/read <file>`): drop `.md`, `.txt` or `.pdf` files into `library/`.
- **Memory** (`/wrap`): writes a log entry, adds review items, updates your profile and
  adds new knowledge-map entries. Review intervals grow 1 → 3 → 7 → 14 → 30 → 60 days
  when you remember an item, and reset to 1 day when you don't.

It uses Claude Opus 5.5 by default (`/settings model <id>` to change). **Refusal
fallback** is on: if Claude declines a request, the API automatically retries on a
fallback model. Cost is roughly a few cents per conversation turn; prompt caching keeps
the large knowledge base cheap after the first message.

### 3. Claude app or LibreChat

```bash
python -m sarva export     # → dist/sarva-prompt.md (persona + knowledge + your profile)
```

- **Claude app:** see [`claude-ai-project/instructions.md`](claude-ai-project/instructions.md).
- **LibreChat:** see [`integrations/librechat/README.md`](integrations/librechat/README.md).

---

## What's inside

| Path | What it is |
|---|---|
| `prompts/persona.md` | Who Sarva is and how it talks: bilingual, short turns, always asks back, cross-domain "そういえば…" connections, honest about uncertainty |
| `knowledge/` | Topic maps for 10 domains plus a **connections** map. They are seeds for conversation; Claude's own knowledge fills in the rest. |
| `journal/` | Sarva's memory of you: `profile.md`, `settings.json`, `log.md`, `review.md` |
| `library/` | Your own documents to discuss |
| `.claude/commands/` | The slash commands (shared by Claude Code and the app) |
| `sarva/` | The app: `core.py` (conversation engine), `web.py` + `static/` (chat page), `cli.py`, `journal.py`, `prompt.py` |

## Ideas borrowed from other projects

This project combines the best ideas from several open-source projects. It is written from
scratch and copies no code from them.

| Idea | Inspired by |
|---|---|
| Self-hosted chat page usable from your phone | [LibreChat](https://github.com/LibreChat-AI/LibreChat), [Open WebUI](https://github.com/open-webui/open-webui) |
| Persistent learner memory, discussing your own documents | [DeepTutor](https://github.com/HKUDS/DeepTutor) |
| Configurable depth and teaching style | [Mr. Ranedeer AI Tutor](https://github.com/JushBJJ/Mr.-Ranedeer-AI-Tutor) |
| Tutor as Claude Code skills / slash commands | [claude-tutor](https://awesome.ecosyste.ms/projects/github.com%2Fjeff7712%2Fclaude-tutor) and similar Claude Code learning skills |
| Socratic questioning | Anthropic's Learning Mode, and Socrates himself |

## Growing the knowledge base

Every `knowledge/*.md` file is a list of one-line entries. Add your own any time, or let
Sarva add new concepts and connections during `/wrap`. The more you talk, the richer the
map gets.
