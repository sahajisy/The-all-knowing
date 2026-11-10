# The All-Knowing — 物知りの友

A daily **conversational learning companion** built on Claude. Instead of reading
Wikipedia pages, you *talk* with "Sensei" (先生) — someone who seems to know everything —
in Japanese or English, two ways, like a conversation between people.

> **You:** 日本の暮らしについて話したい
>
> **Sensei:** いいですね！じゃあ「もったいない」から始めましょうか。実はこの言葉、ケニアの
> ノーベル平和賞受賞者ワンガリ・マータイさんが世界に広めたんです。そういえば、細胞にも
> 「もったいない」の仕組みがあって、大隅良典さんがノーベル賞を取ったオートファジーがまさに
> それなんですよ。…ちなみに、普段の生活で「もったいない」と感じるのはどんな時ですか？

## How it works

| Piece | What it does |
|---|---|
| `CLAUDE.md` | Sensei's personality and conversation rules (bilingual, short turns, always asks back, makes cross-domain connections, honest about uncertainty) |
| `knowledge/` | Topic maps for 10 domains + a **connections** map — seeds for "そういえば…" jumps. Claude's own broad knowledge fills in the details. |
| `journal/` | Sensei's memory of you: profile, a log of every session, and a spaced-repetition review queue |
| `.claude/commands/` | Slash commands for the daily routine |
| `claude-ai-project/` | Instructions to use the same Sensei in the Claude app (phone/web) |

## Daily use (Claude Code)

Open this repository in Claude Code (terminal, desktop app, or claude.ai/code) and type:

| Command | 使い方 |
|---|---|
| `/daily` | 今日の話題 — a fresh topic from a rotating domain, opened with a hook |
| `/talk <topic>` | Talk about anything: `/talk 日本の銭湯文化`, `/talk Kubernetes` |
| `/dive <topic>` | Deeper guided exploration: `/dive 量子コンピュータ` |
| `/surprise` | A random surprising fact, then discussion |
| `/connect <A> <B>` | Hidden links: `/connect 寿司 blockchain` |
| `/quiz` | Friendly spaced-repetition review of past topics |
| `/lang ja\|en\|mix` | Switch language |
| `/wrap` | Recap + save the session to the journal (commits & pushes so memory persists) |

Or just start talking — no command needed.

### A suggested 15-minute routine
1. `/daily` (or `/quiz` every few days)
2. Chat — ask "why?", disagree, share your own experience
3. `/wrap`

## Daily use (Claude app)

See [`claude-ai-project/instructions.md`](claude-ai-project/instructions.md) to set up a
Claude Project with the same personality and knowledge maps — handy on your phone.

## Growing the knowledge base

Every `knowledge/*.md` file is a list of one-line entries. Add your own any time, or let
Sensei add new concepts and connections during `/wrap`. The more you talk, the richer the map gets.
