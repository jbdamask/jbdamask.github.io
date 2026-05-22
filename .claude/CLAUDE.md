## Issue Tracking

This project uses **bd** (beads) as its issue tracker. See [AGENTS.md](../../AGENTS.md) for detailed agent instructions and workflow.

## Current Ground Rules

- Run `bd prime` before doing tracked work (after compaction, clear, or a new session).
- Beads uses **Dolt** as the issue database. Use `bd dolt push` / `bd dolt pull` for issue data sync. Do **not** use export/import as a routine git workflow, and do **not** use the old `bd sync` command (it no longer exists in current bd versions).
- Follow [AGENTS.md](../../AGENTS.md) for the full workflow, including the "Landing the Plane" session-close protocol.
- If this file conflicts with [AGENTS.md](../../AGENTS.md), trust AGENTS.md and update this file by removing the duplicate.
