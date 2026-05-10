---
title: Talk About It
tool_url: /tools/talk-about-it.html
excerpt: Convene a small panel of Claude agents — each with their own perspective — and watch them discuss your topic in real time.
permalink: /tools/talk-about-it/
---

# Talk About It

A single-page web tool that spins up 1–5 Claude Sonnet agents (the "panel"), each playing a distinct role chosen for the topic, and lets you watch them discuss it in a serial chat. A separate Claude moderator routes the conversation between rounds — relaying quotes between panelists, pausing to ask you clarifying questions when the panel needs your input, and producing a wrap-up report at the end.

It's a browser port of the [`talk-about-it` Claude Code skill](https://github.com/jbdamask/claude-code-skills), built on the Anthropic Messages API with direct browser access.

## Purpose

Useful when you want **multiple perspectives** on a topic instead of a single answer:

- Gut-checking a design or architecture decision (senior engineer vs. ops vs. PM)
- Exploring a trade-off space (proponent vs. opponent vs. pragmatist)
- Brainstorming through specialists (e.g. perennial specialist, annual specialist, garden designer for "best flowers for a small shady garden")
- Walking through a plan with a panel of stakeholders before committing

It is **not** a research tool, and it is not for adversarial review (use a debate workflow for that). It's a structured group chat that explores a topic from multiple angles.

## Setup

1. Get an Anthropic API key at [console.anthropic.com](https://console.anthropic.com/settings/keys).
2. Open the tool, expand **Settings**, paste the key in, and click the save icon. The key is stored only in your browser's `localStorage` and sent directly to `api.anthropic.com`.
3. (Optional) Pick a model — Sonnet 4.6 is the default. Haiku 4.5 is cheaper; Opus 4.7 is slower and smarter.
4. (Optional) Adjust **Max rounds** — a hard cap on conversation rounds before the moderator is forced to wrap up.

## Usage

1. Enter a one-sentence **topic** (e.g. "Best flowers for a small, shady garden in New England").
2. (Optional) Paste **context** — background, prior decisions, constraints, or what you want out of the conversation.
3. Choose **panel size** (1–5) and **roles**:
   - *Auto* — the moderator proposes specific roles tailored to the topic.
   - *Custom* — you provide a comma-separated list of names (e.g. "Perennial Specialist, Annual Specialist, Garden Designer").
4. Click **Start session**. The moderator may ask 1–3 clarifying questions and propose roles. Edit them inline if you want, then **Confirm and start panel**.
5. Watch each panelist's response stream into the chat in turn. Each panelist gets their own color and byline.
6. **Interject** anytime via the textbox at the bottom (Cmd/Ctrl+Enter to send) — your message goes to the moderator and is routed into the next round.
7. Click **Wrap up** when you're ready for a summary, or let the moderator decide the panel has run its course.
8. Click **Export** to download the entire chat as a Markdown file (panel roster, every turn attributed by name, and the wrap-up report).

## Behavior notes

- **Serial replies.** Panelists speak one at a time so the conversation reads like a real chat instead of three streams firing in parallel.
- **Scroll-friendly.** The page only auto-scrolls when you're already near the bottom. Scroll up to read previous turns and a "Jump to latest" pill appears when new content lands offscreen.
- **Moderator can ask you questions.** If a panelist needs information only you have, the moderator pauses the loop and surfaces the question in a modal. Your answer goes back into the next round.
- **Live token + cost tracking.** Bottom-right shows running token usage and a rough USD estimate based on the selected model's published rates.

## Requirements

- A modern browser with JavaScript enabled.
- An Anthropic API key with available credits.
- Internet connection.

## Privacy & cost

Your API key never leaves the browser except to talk to Anthropic directly — there is no server. The page uses the `anthropic-dangerous-direct-browser-access` header, which is fine for personal BYOK use but means anyone you share the page with would need their own key (and could read theirs from devtools).

A typical 3-panelist 6–10 round session on Sonnet 4.6 runs a few cents to ~$0.30 depending on context length. Watch the cost display under the status bar — it updates live.
