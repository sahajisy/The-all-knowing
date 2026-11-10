# Using Sarva in LibreChat

[LibreChat](https://github.com/LibreChat-AI/LibreChat) is a popular open-source,
self-hosted chat interface. If you already run it (or prefer its interface, accounts and
mobile layout), you can turn Sarva into a LibreChat **Agent**.

## Steps

1. **Install LibreChat** by following its official guide
   (https://www.librechat.ai/docs). The Docker Compose setup is the simplest.
2. **Enable Anthropic**: add your key to LibreChat's `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
   Check LibreChat's docs for the Anthropic endpoint and how to list models, and make sure
   `claude-opus-5-5` (or another current Claude model) is available.
3. **Export Sarva's prompt** from this repository:
   ```bash
   python -m sarva export          # writes dist/sarva-prompt.md
   ```
4. In LibreChat, open **Agents → Create agent**:
   - **Name:** `Sarva`
   - **Model:** Anthropic → `claude-opus-5-5`
   - **Instructions:** paste the contents of `dist/sarva-prompt.md`
   - **Files / knowledge** (optional): upload documents you'd like to discuss (your `library/`)
5. Start a chat with the agent and say 「今日の話題は？」 or "/daily".

## Keeping memory in sync

LibreChat can't write to this repository's `journal/`. At the end of a chat, say
**"wrap up"**. Sarva replies with a log entry. Paste it under `## Sessions` in
`journal/log.md`, or simply re-run `python -m sarva export` after using the Sarva app
or Claude Code so the agent's instructions include your latest profile and log.

> The exported prompt is a snapshot. Re-export and update the agent's instructions
> occasionally (for example, weekly) so Sarva remembers recent sessions.
