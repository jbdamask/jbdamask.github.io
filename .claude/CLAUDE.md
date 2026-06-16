## Issue Tracking

This project uses **bd** (beads) as its issue tracker. See [AGENTS.md](../../AGENTS.md) for detailed agent instructions and workflow.

## Adding Blog Posts

- Add a self-contained HTML page as a post with `python scripts/add_html_post.py <file>`
  (MHTML: `scripts/convert_mhtml.py`). These scripts **automatically** generate
  an on-brand social card and wire the `image:` front matter — do not hand-add
  posts to `_posts/` in a way that skips this. See [ADDING_HTML_PAGES.md](../../ADDING_HTML_PAGES.md).
- Every direct post (content hosted in this repo) must have a social card.
  Hand-written markdown posts: run `python scripts/make_social_card.py --post <file>`
  (or `--all` to backfill any post missing one). A bespoke `image:` is never overwritten.
- The site favicon (Amroja icon) and canonical domain (`johndamask.com`) are wired
  globally — no per-post action needed.

## Current Ground Rules

- Run `bd prime` before doing tracked work (after compaction, clear, or a new session).
- Beads uses **Dolt** as the issue database. Use `bd dolt push` / `bd dolt pull` for issue data sync. Do **not** use export/import as a routine git workflow, and do **not** use the old `bd sync` command (it no longer exists in current bd versions).
- Follow [AGENTS.md](../../AGENTS.md) for the full workflow, including the "Landing the Plane" session-close protocol.
- If this file conflicts with [AGENTS.md](../../AGENTS.md), trust AGENTS.md and update this file by removing the duplicate.
