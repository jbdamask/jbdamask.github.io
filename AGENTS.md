# Agent Instructions

This project uses **bd** (beads) for issue tracking. Run `bd prime` at the start of any session (after compaction, clear, or a new session) to load the workflow context.

## Quick Reference

```bash
bd prime              # Load workflow context (run at session start)
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim                  # Atomically claim work
bd update <id> --status in_progress     # Or set status explicitly
bd close <id>         # Complete work
bd dolt push          # Push issue DB to remote (Dolt)
bd dolt pull          # Pull issue DB from remote (Dolt)
```

> **Note**: `bd sync` no longer exists in current bd versions. Beads now uses **Dolt** as the issue database and auto-commits every write to Dolt history. Use `bd dolt push` / `bd dolt pull` for remote sync.

## Beads Tasks

When creating Beads tasks, always include Acceptance Criteria.

**Acceptance Criteria: Must Be Verifiable.** Each criterion must be something that can be objectively checked, not something vague.

### Good criteria (verifiable)
- "Add status column to tasks table with default 'pending'"
- "Filter dropdown has options: All, Active, Completed"
- "Clicking delete shows confirmation dialog"
- "Typecheck passes"
- "Tests pass"

### Bad criteria (vague)
- "Works correctly"
- "User can do X easily"
- "Good UX"
- "Handles edge cases"

### Always include as final criterion
- "Typecheck passes"

### For tasks with testable logic, also include
- "Tests pass"

### For tasks that change UI, also include
- "Verify in browser"

## Agent Warning: Interactive Commands

**DO NOT use `bd edit`** — it opens an interactive editor (`$EDITOR`) which AI agents cannot use.

Use `bd update` with flags instead:

```bash
bd update <id> --description "new description"
bd update <id> --title "new title"
bd update <id> --design "design notes"
bd update <id> --notes "additional notes"
bd update <id> --acceptance "acceptance criteria"

# Use stdin for descriptions with special characters (backticks, !, nested quotes)
echo 'Description with `backticks` and "quotes"' | bd create "Title" --description=-
echo 'Updated text' | bd update <id> --description=-
```

## Non-Interactive Shell Commands

**ALWAYS use non-interactive flags** with file operations to avoid hanging on confirmation prompts.

Shell commands like `cp`, `mv`, and `rm` may be aliased to include `-i` (interactive) mode on some systems, causing the agent to hang indefinitely waiting for y/n input.

**Use these forms instead:**

```bash
cp -f source dest           # NOT: cp source dest
mv -f source dest           # NOT: mv source dest
rm -f file                  # NOT: rm file

# For recursive operations
rm -rf directory            # NOT: rm -r directory
cp -rf source dest          # NOT: cp -r source dest
```

**Other commands that may prompt:**
- `scp` / `ssh` — use `-o BatchMode=yes` to fail instead of prompting
- `apt-get` — use `-y` flag
- `brew` — use `HOMEBREW_NO_AUTO_UPDATE=1` env var

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** — Create bd issues for anything that needs follow-up
2. **Run quality gates** (if code changed) — Tests, linters, builds
3. **Update issue status** — Close finished work, update in-progress items
4. **PUSH TO REMOTE** — This is MANDATORY:
   ```bash
   git pull --rebase
   git push
   bd dolt push        # Sync issue DB to Dolt remote
   git status          # MUST show "up to date with origin"
   ```
5. **Clean up** — Clear stashes, prune remote branches
6. **Verify** — All changes committed AND pushed (both code and beads)
7. **Hand off** — Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing — that leaves work stranded locally
- NEVER say "ready to push when you are" — YOU must push
- If push fails, resolve and retry until it succeeds

<!-- BEGIN BEADS INTEGRATION -->
## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Why bd?

- Dependency-aware: Track blockers and relationships between issues
- Git-friendly: Dolt-powered version control with native sync
- Agent-optimized: JSON output, ready work detection, discovered-from links
- Prevents duplicate tracking systems and confusion

### Quick Start

**Check for ready work:**

```bash
bd ready --json
```

**Create new issues:**

```bash
bd create "Issue title" --description="Detailed context" -t bug|feature|task -p 0-4 --json
bd create "Issue title" --description="What this issue is about" -p 1 --deps discovered-from:bd-123 --json

# Use stdin for descriptions with special characters (backticks, !, nested quotes)
echo 'Description with `backticks` and "quotes"' | bd create "Title" --description=- --json
```

**Claim and update:**

```bash
bd update <id> --claim --json
bd update bd-42 --priority 1 --json
```

**Complete work:**

```bash
bd close bd-42 --reason "Completed" --json
```

### Issue Types

- `bug` — Something broken
- `feature` — New functionality
- `task` — Work item (tests, docs, refactoring)
- `epic` — Large feature with subtasks
- `chore` — Maintenance (dependencies, tooling)

### Priorities

- `0` — Critical (security, data loss, broken builds)
- `1` — High (major features, important bugs)
- `2` — Medium (default, nice-to-have)
- `3` — Low (polish, optimization)
- `4` — Backlog (future ideas)

### Workflow for AI Agents

1. **Check ready work**: `bd ready` shows unblocked issues
2. **Read execution metadata first**: before deciding local vs delegated work, model, or reasoning level, inspect structured metadata:
   ```bash
   bd show <id> --json | jq '.[0] | {id,title,metadata,description,notes}'
   ```
   The execution metadata keys `execution_agent_type`, `execution_suggested_model`, `execution_reasoning_effort`, `execution_mode`, and `execution_parallel_group` are authoritative hints when present. Use description and notes as fallback context.
3. **Claim your task atomically**: `bd update <id> --claim`
4. **Work on it**: Implement, test, document
5. **Discover new work?** Create linked issue:
   - `bd create "Found bug" --description="Details about what was found" -p 1 --deps discovered-from:<parent-id>`
6. **Complete**: `bd close <id> --reason "Done"`

### Auto-Sync (Dolt Backend)

bd automatically syncs via Dolt:

- Each write auto-commits to Dolt history
- Use `bd dolt push` / `bd dolt pull` for remote sync
- No manual export/import needed
- **Do not** call the old `bd sync` command — it has been removed

### Task Verification (CRITICAL)

**Never close a task without verifying ALL acceptance criteria.**

Before marking any task complete:

1. Run `bd show <id>` to see the full acceptance criteria
2. Verify each criterion individually against the actual code/implementation
3. Run verification commands (typecheck, tests, browser check) if listed
4. Only close when ALL criteria pass — partial completion = task stays open

**Common mistakes to avoid:**
- Assuming a task is done because related code exists
- Closing a frontend task because the backend Lambda exists
- Skipping "Typecheck passes" or "Verify in browser" criteria
- Closing without reading the acceptance criteria first

**If any criterion fails:** The task is NOT complete. Either fix the gaps or leave it open.

### Important Rules

- Use bd for ALL task tracking
- Always use `--json` flag for programmatic use
- Link discovered work with `discovered-from` dependencies
- Check `bd ready` before asking "what should I work on?"
- Do NOT create markdown TODO lists
- Do NOT use external issue trackers
- Do NOT duplicate tracking systems

<!-- END BEADS INTEGRATION -->

## Using bv as an AI sidecar

`bv` ([beads_viewer](https://github.com/Dicklesworthstone/beads_viewer)) is a graph-aware triage engine for Beads projects. Instead of parsing the issue DB or hallucinating graph traversal, use robot flags for deterministic, dependency-aware outputs with precomputed metrics (PageRank, betweenness, critical path, cycles, HITS, eigenvector, k-core).

**Scope boundary:** bv handles *what to work on* (triage, priority, planning). For agent-to-agent coordination (messaging, work claiming, file reservations), use [MCP Agent Mail](https://github.com/Dicklesworthstone/mcp_agent_mail).

**⚠️ CRITICAL: Use ONLY `--robot-*` flags.** Bare `bv` launches an interactive TUI that blocks your session.

### The Workflow: Start With Triage

**`bv --robot-triage` is your single entry point.** It returns everything you need in one call:
- `quick_ref`: at-a-glance counts + top 3 picks
- `recommendations`: ranked actionable items with scores, reasons, unblock info
- `quick_wins`: low-effort high-impact items
- `blockers_to_clear`: items that unblock the most downstream work
- `project_health`: status/type/priority distributions, graph metrics
- `commands`: copy-paste shell commands for next steps

```bash
bv --robot-triage        # THE MEGA-COMMAND: start here
bv --robot-next          # Minimal: just the single top pick + claim command

# Token-optimized output (TOON) for lower LLM context usage:
bv --robot-triage --format toon
export BV_OUTPUT_FORMAT=toon
bv --robot-next
```

### Other Commands

**Planning:**

| Command | Returns |
|---------|---------|
| `--robot-plan` | Parallel execution tracks with `unblocks` lists |
| `--robot-priority` | Priority misalignment detection with confidence |

**Graph Analysis:**

| Command | Returns |
|---------|---------|
| `--robot-insights` | Full metrics: PageRank, betweenness, HITS, eigenvector, critical path, cycles, k-core, articulation points, slack |
| `--robot-label-health` | Per-label health: `health_level`, `velocity_score`, `staleness`, `blocked_count` |
| `--robot-label-flow` | Cross-label dependency: `flow_matrix`, `dependencies`, `bottleneck_labels` |
| `--robot-label-attention [--attention-limit=N]` | Attention-ranked labels by: (pagerank × staleness × block_impact) / velocity |

**History & Change Tracking:**

| Command | Returns |
|---------|---------|
| `--robot-history` | Bead-to-commit correlations |
| `--robot-diff --diff-since <ref>` | Changes since ref |

**Other Commands:**

| Command | Returns |
|---------|---------|
| `--robot-burndown <sprint>` | Sprint burndown, scope changes, at-risk items |
| `--robot-forecast <id\|all>` | ETA predictions with dependency-aware scheduling |
| `--robot-alerts` | Stale issues, blocking cascades, priority mismatches |
| `--robot-suggest` | Hygiene: duplicates, missing deps, label suggestions, cycle breaks |
| `--robot-graph [--graph-format=json\|dot\|mermaid]` | Dependency graph export |
| `--export-graph <file.html>` | Self-contained interactive HTML visualization |

### Scoping & Filtering

```bash
bv --robot-plan --label backend              # Scope to label's subgraph
bv --robot-insights --as-of HEAD~30          # Historical point-in-time
bv --recipe actionable --robot-plan          # Pre-filter: ready to work (no blockers)
bv --recipe high-impact --robot-triage       # Pre-filter: top PageRank scores
bv --robot-triage --robot-triage-by-track    # Group by parallel work streams
bv --robot-triage --robot-triage-by-label    # Group by domain
```

### Understanding Robot Output

**All robot JSON includes:**
- `data_hash` — Fingerprint of source data (verify consistency across calls)
- `status` — Per-metric state: `computed|approx|timeout|skipped` + elapsed ms
- `as_of` / `as_of_commit` — Present when using `--as-of`

**Two-phase analysis:**
- **Phase 1 (instant):** degree, topo sort, density — always available immediately
- **Phase 2 (async, 500ms timeout):** PageRank, betweenness, HITS, eigenvector, cycles — check `status` flags

**For large graphs (>500 nodes):** Some metrics may be approximated or skipped. Always check `status`.

### jq Quick Reference

```bash
bv --robot-triage | jq '.quick_ref'                        # At-a-glance summary
bv --robot-triage | jq '.recommendations[0]'               # Top recommendation
bv --robot-plan | jq '.plan.summary.highest_impact'        # Best unblock target
bv --robot-insights | jq '.status'                         # Check metric readiness
bv --robot-insights | jq '.Cycles'                         # Circular deps (must fix!)
bv --robot-label-health | jq '.results.labels[] | select(.health_level == "critical")'
```

**Performance:** Phase 1 instant, Phase 2 async (500ms timeout). Prefer `--robot-plan` over `--robot-insights` when speed matters. Results cached by data hash.

Use `bv` instead of parsing the beads DB directly — it computes PageRank, critical paths, cycles, and parallel tracks deterministically.
