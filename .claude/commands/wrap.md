---
description: End the session — summarize, update the journal, and save it
---

Wrap up this session.

1. Give the user a short, friendly recap in the session's language:
   - 3–5 key things we talked about / learned,
   - one connection that came up,
   - one question to think about until next time.
2. Update the journal files (use today's date, YYYY-MM-DD):
   - `journal/log.md` — append a new entry at the TOP of the "Sessions" list using the
     template in that file.
   - `journal/review.md` — add 2–4 of the most important facts/ideas with
     `next review` = tomorrow.
   - `journal/profile.md` — add anything new learned about the user (interests, job,
     opinions, places they've been, what they already knew well).
   - `knowledge/*.md` — if a great new concept or connection came up that isn't in the
     maps, add a one-line entry to the right file.
3. Save: `git add journal knowledge && git commit -m "Learning log: <date> — <topics>"`
   then `git push`. (If push fails due to the network, retry a few times.)
4. Say goodbye like a friend (「今日も楽しかったです。またね！」).
