---
description: Show or change learner settings (depth, style, length, language)
argument-hint: [key value]
---

Learner settings live in `journal/settings.json` (see "Learner settings" in `prompts/persona.md`).

Arguments: **$ARGUMENTS**

- With no arguments: show the current settings in a short friendly table, with the options
  for each (depth 1–5; style balanced/socratic/storyteller/debate/quick-facts; turn_length
  short/medium/long; language auto/ja/en/mix), and ask if they want to change anything.
- With `key value` (e.g. `depth 5`, `style socratic`): validate, update `journal/settings.json`,
  confirm in one line, and apply it from your next message.
