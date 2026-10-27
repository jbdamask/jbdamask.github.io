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
ToolSearch select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__browser_batch,mcp__claude-in-chrome__tabs_close_mcp
```

Then `mcp__claude-in-chrome__tabs_context_mcp` with `createIfEmpty: true` to get/create a tab.

### 2. Collect existing URNs from the YAML

Read `_data/external-posts.yml`. For every `url:` that looks like `urn:li:activity:<id>` or `-activity-<id>-`, extract the 19-digit activity ID into a set. Skip these on insert.

### 3. Scrape the recent-activity page

Navigate the tab to `https://www.linkedin.com/in/johndamask/recent-activity/all/`.

Extract the top-N activity IDs (default 20, user can override). LinkedIn no longer puts `data-urn` attributes on feed items, so pull the IDs from the raw page HTML instead. They appear in document order, newest-first:

```javascript
await new Promise(r => setTimeout(r, 3000));  // let the feed hydrate
const html = document.documentElement.outerHTML;
JSON.stringify([...new Set(
  [...html.matchAll(/(?:urn:li:activity:|urn%3Ali%3Aactivity%3A|activity-)(\d{19})/g)].map(m => m[1])
)].slice(0, 20))
```

This returns e.g. `["7512530513736183808", ...]`. If it returns an empty list, check `document.body.innerText` for a login screen (see edge cases).

### 4. Dates

Use the date LinkedIn displays on the post page (e.g. "Sep 22"; for relative times like "21h" or "Yesterday", count back from today). That is the user's local date.

The activity ID also encodes a UTC timestamp (`Number(BigInt(id) >> 22n)` → ms epoch). Use it to sanity-check the year or for ordering, but don't use it for the `date` field: a late-evening US post lands on the next day in UTC.

### 5. For each new ID (not in the existing set), fetch post text

Use `mcp__claude-in-chrome__browser_batch` to visit several posts in one call: a `navigate` to `https://www.linkedin.com/feed/update/urn:li:activity:<id>/` followed by a `javascript_tool` call per post. The old CSS class selectors (`.feed-shared-text` etc.) no longer match, so read the page text starting at the "Feed post" marker:

```javascript
await new Promise(r => setTimeout(r, 2500));
const t = (document.querySelector('main') || document.body).innerText;
t.slice(t.indexOf('Feed post'), t.indexOf('Feed post') + 1500)
```

The result starts with the author line ("John Damask • You"), then the displayed date, then the post body. Results get truncated around 1,500 characters per post. That's enough for a title and excerpt.

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
git pull --rebase
git push
```

Pull before pushing: automated jobs commit Twitter and Substack feed updates to `main` often, so a plain push is usually rejected.

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
- **Group posts**: Posts John made in a LinkedIn group show the group name (e.g. "AI in Everyday Life") above the author line. These are his posts, but they often repeat a story he also posted on his own feed. Flag group posts that duplicate a main-feed post, and ask whether to include them.
- **Videos without text**: If the post body is very short (e.g. just a video), ask the user for a title/excerpt rather than guessing.
- **LinkedIn blocks / expired session**: If scraping returns "This post cannot be displayed" or shows a login screen, tell the user to re-authenticate in Chrome.
- **Chrome auto-download blocks**: Not relevant here because no downloads are needed. If a future change adds image fetching, note that Chrome blocks multiple auto-downloads from linkedin.com after the first — would need `chrome://settings/content/automaticDownloads` permission for the site.
