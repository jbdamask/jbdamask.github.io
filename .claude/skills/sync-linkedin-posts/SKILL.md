---
name: sync-linkedin-posts
description: Sync recent LinkedIn posts from johndamask's profile into _data/external-posts.yml. Use when the user says "sync my linkedin posts", "pull in new linkedin posts", "check linkedin for new blog entries", "update external-posts from linkedin", or otherwise asks to refresh the LinkedIn section of the blog feed. Scrapes https://www.linkedin.com/in/johndamask/recent-activity/all/ via the Claude-in-Chrome MCP, skips URNs already present in the YAML, appends new entries, validates, commits, and pushes.
---

# sync-linkedin-posts

Sync recent LinkedIn posts into `_data/external-posts.yml` so they appear in the site's unified blog feed.

## Prerequisites

- Claude-in-Chrome MCP must be available (tools `mcp__claude-in-chrome__*`).
- The user must be logged into LinkedIn in Chrome (the skill relies on their session).
- Working directory is the root of this Jekyll repo.

## Workflow

### 1. Load browser tools and ensure a tab

Deferred browser tools must be loaded before use. Run once per session:

```
ToolSearch select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__javascript_tool
```

Then `mcp__claude-in-chrome__tabs_context_mcp` with `createIfEmpty: true` to get/create a tab.

### 2. Collect existing URNs from the YAML

Read `_data/external-posts.yml`. For every `url:` that looks like `urn:li:activity:<id>` or `-activity-<id>-`, extract the 19-digit activity ID into a set. Skip these on insert.

### 3. Scrape the recent-activity page

Navigate the tab to `https://www.linkedin.com/in/johndamask/recent-activity/all/`.

Extract the top-N URNs (default 20, user can override):

```javascript
JSON.stringify(
  Array.from(document.querySelectorAll('[data-urn]'))
    .map(e => e.getAttribute('data-urn'))
    .filter(u => u && u.includes('activity'))
    .slice(0, 20)
)
```

This returns an ordered list newest-first, e.g. `["urn:li:activity:7453111529304158209", ...]`.

### 4. Compute dates from URN snowflake IDs

LinkedIn activity IDs encode a timestamp in the high bits. Shift right 22 for ms epoch:

```javascript
const ts = Number(BigInt(id) >> 22n);
new Date(ts).toISOString();  // → use YYYY-MM-DD for the date field
```

### 5. For each new URN (not in the existing set), fetch post text

Navigate to `https://www.linkedin.com/feed/update/urn:li:activity:<id>/`. Wait ~2.5 seconds for hydration, then extract the post body:

```javascript
new Promise(r => setTimeout(() => {
  const c = document.querySelector('.feed-shared-inline-show-more-text, .update-components-update-v2__commentary, .feed-shared-text');
  r(c ? c.innerText : 'not found');
}, 2500))
```

If the page returns "This post cannot be displayed", retry using the slug URL the user provided (format: `https://www.linkedin.com/posts/johndamask_<slug>-activity-<id>-<suffix>/`). Some feeds only render via the slug URL.

**Crafting title and excerpt:**
- Title: short, descriptive (5–10 words). Usually draws from the post's first sentence or headline idea. Don't copy the full first line verbatim if it's long.
- Excerpt: 1–3 sentences (aim for 30–60 words). Capture the point without quoting the whole post. Use em dashes sparingly; avoid AI-slop phrasing.
- Prefer the user's own framing. If the post has an obvious hook ("Today I shipped X"), lead with it.

If the user supplies a specific title for a post (e.g. "call it AWS Quick Endpoints and Claude Channels"), use it exactly.

### 6. Append entries to `_data/external-posts.yml`

Entries go in reverse chronological order. The file has no date-sorting at build time — the JS frontend merges feeds and sorts by date — but keeping the file ordered makes diffs readable.

Entry format (exactly):

```yaml
- title: "Short descriptive title"
  source: linkedin
  url: https://www.linkedin.com/feed/update/urn:li:activity:<ID>/
  date: YYYY-MM-DD
  excerpt: "1–3 sentence summary."
  image: ""
```

Notes:
- `image: ""` is correct. The site does not render per-post thumbnails; the source badge (`LINKEDIN`) is what displays. Do not spend time fetching thumbnail images.
- Use double-quoted strings for `title` and `excerpt` so em dashes and apostrophes render cleanly.
- The canonical feed URL works for all posts. Only fall back to the slug URL if the canonical returns "post cannot be displayed".

Insert each new entry at the correct date position (above the next-older existing entry).

### 7. Validate YAML parses

```bash
ruby -ryaml -rdate -e "puts YAML.load_file('_data/external-posts.yml', permitted_classes: [Date, Time]).size"
```

Must print an integer (new total count) with no errors. If it fails, fix the entry and re-validate.

### 8. Commit and push

```bash
git add _data/external-posts.yml
git commit -m "Add N recent LinkedIn posts to external feed"
git push
```

Use a single commit for all new posts from one sync run. Do not attribute to Claude Code in the commit message (project convention).

## Report

After pushing, tell the user:
- How many posts were added
- Their titles and dates
- How many existing URNs were skipped
- The commit hash

## Edge cases

- **Duplicate with another source**: The repo has a separate `_data/nowigetit-posts.yml` for blog.nowigetit.us posts. A LinkedIn post about a Now I Get It! launch can legitimately duplicate a nowigetit entry (same event, different channel). Flag this to the user and ask whether to include both — don't silently dedupe across files.
- **Reposts of someone else's content**: The recent-activity page includes reposts. Skip any post where the author is not John Damask (check for "John Damask • You" marker near the top of the post block).
- **Videos without text**: If the post body is very short (e.g. just a video), ask the user for a title/excerpt rather than guessing.
- **LinkedIn blocks / expired session**: If scraping returns "This post cannot be displayed" or shows a login screen, tell the user to re-authenticate in Chrome.
- **Chrome auto-download blocks**: Not relevant here because no downloads are needed. If a future change adds image fetching, note that Chrome blocks multiple auto-downloads from linkedin.com after the first — would need `chrome://settings/content/automaticDownloads` permission for the site.
