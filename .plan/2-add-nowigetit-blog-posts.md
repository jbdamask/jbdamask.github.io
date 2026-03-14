# Plan: Add Now I Get It! Blog Posts to johndamask.com

## Context
GitHub Issue #2: The user blogs on the [Now I Get It!](https://nowigetit.us/blog) platform and wants those posts aggregated into johndamask.com alongside Substack, Twitter, LinkedIn, and Jekyll posts. The site already has a well-established pattern for fetching and displaying posts from multiple sources.

The Now I Get It! blog has a working RSS feed at `https://nowigetit.us/blog/feed.xml` with 25+ entries.

## Resolved Questions

1. **RSS date format**: Confirmed standard RFC 822 (`Sat, 14 Mar 2026 00:00:00 GMT`) — same format the Substack parser already handles. The same `datetime.strptime` call works.
2. **Images**: The RSS feed contains NO images — no `<content:encoded>`, no `<enclosure>`, no `<media:content>`. Only `<description>` text is present. Per user direction, the `image` field will always be empty string. Posts will render in the text-only card format (no thumbnail), same as blog posts without images.
3. **No proxy needed**: The feed is publicly accessible. GitHub Actions fetches server-side so CORS is irrelevant. No CloudFlare Worker required.
4. **RSS feed stability**: Script handles failures gracefully — exits with code 1 and preserves existing data file.
5. **Branding**: The source badge will be branded as **"Now I Get It! DevLog"** using the site's lightbulb logo (`https://nowigetit.us/logo.png`) with black background (`#0a0d17`) and gold text (`#e8a838`), matching the Now I Get It! site's dark+gold aesthetic. Badge size matches existing Substack/LinkedIn/Blog badges.

## Recommended Approach
Follow the existing Substack pattern — a Python fetch script, a YAML data file, a GitHub Actions workflow, and frontend integration (hidden data divs + JS extraction + rendering with branded source badge). No image extraction needed.

## Changes

### 1. `scripts/fetch_nowigetit.py` (NEW)
- New Python script modeled on `scripts/fetch_substack.py`
- Fetches RSS from `https://nowigetit.us/blog/feed.xml`
- Parses standard RSS XML: `<title>`, `<link>`, `<pubDate>`, `<description>`, `<guid>`
- No image extraction (feed has no images)
- Sets `source: 'nowigetit'`, `image: ''`
- Date parsing: `datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")`
- Outputs to `_data/nowigetit-posts.yml`
- Uses same merge/dedup pattern (URL-keyed dict) to preserve history

### 2. `_data/nowigetit-posts.yml` (NEW, auto-generated)
- YAML format:
  ```yaml
  - title: 'Post Title'
    source: nowigetit
    url: https://nowigetit.us/blog/post-slug.html
    date: '2026-03-14'
    excerpt: 'First 200 chars of description...'
    image: ''
  ```

### 3. `.github/workflows/fetch-nowigetit.yml` (NEW)
- GitHub Actions workflow modeled on `fetch-substack.yml`
- Name: `"Fetch Now I Get It Posts"`
- Schedule: hourly (`0 * * * *`) + manual dispatch
- Steps: checkout → setup Python 3.11 → install deps (`requests PyYAML`) → run script → commit if changed
- Commit message: `"Update Now I Get It posts"`

### 4. `.github/workflows/jekyll.yml` (MODIFY)
- Add `"Fetch Now I Get It Posts"` to the `workflow_run.workflows` array:
  ```yaml
  workflows: ["Fetch Substack Posts", "Fetch Twitter Posts", "Fetch Now I Get It Posts"]
  ```

### 5. `index.html` (MODIFY)
- Add hidden data div block for nowigetit posts (after Substack block):
  ```html
  {% if site.data.nowigetit-posts %}
  {% for post in site.data.nowigetit-posts %}
    <div class="nowigetit-post-item"
         data-title="{{ post.title | xml_escape }}"
         data-excerpt="{{ post.excerpt | xml_escape }}"
         data-url="{{ post.url }}"
         data-date="{{ post.date | date_to_xmlschema }}"
         data-image="">
    </div>
  {% endfor %}
  {% endif %}
  ```
- Add CSS for branded `.nowigetit` source badge:
  - Background: `#0a0d17` (Now I Get It! dark)
  - Text color: `#e8a838` (Now I Get It! gold)
  - Includes inline lightbulb icon (small CSS/SVG icon or emoji) before "Now I Get It! DevLog" text
  - Same size as existing `.post-source` badges (padding, font-size, border-radius)

### 6. `assets/js/substack-feed.js` (MODIFY)
- Add `getNowigetitPosts()` function (same pattern as `getSubstackPosts()`, querying `.nowigetit-post-item`)
- Add `nowigetit` source label in `renderCombinedPosts()`:
  ```javascript
  } else if (post.source === 'nowigetit') {
    sourceLabel = '<span class="post-source nowigetit">💡 Now I Get It! DevLog</span>';
  }
  ```
- Include nowigetit posts in the `allPosts` array in `DOMContentLoaded`

### 7. Lightbulb icon for badge (DESIGN DECISION)
- Use a small inline SVG lightbulb or the 💡 emoji as the icon prefix in the badge
- The SVG approach gives more control over color matching (gold stroke on dark background)
- Alternative: download `logo.png` to `assets/images/nowigetit-logo.png` and use as a tiny inline `<img>` in the badge — but SVG/emoji is simpler and more consistent with badge sizing

## Critical Files
| File | Action | Notes |
|------|--------|-------|
| `scripts/fetch_nowigetit.py` | CREATE | RSS fetch + YAML output (no images) |
| `_data/nowigetit-posts.yml` | CREATE (auto) | Generated by fetch script |
| `.github/workflows/fetch-nowigetit.yml` | CREATE | Hourly cron workflow |
| `.github/workflows/jekyll.yml` | MODIFY | Add workflow_run trigger |
| `index.html` | MODIFY | Hidden data divs + branded CSS badge |
| `assets/js/substack-feed.js` | MODIFY | JS extraction + rendering |

## Dependencies & Ordering
1. **`scripts/fetch_nowigetit.py`** — foundation, create first
2. **`_data/nowigetit-posts.yml`** — generated by running script locally for initial seed
3. **`.github/workflows/fetch-nowigetit.yml`** — depends on script existing
4. **`.github/workflows/jekyll.yml`** — depends on workflow name being finalized
5. **`index.html`** + **`assets/js/substack-feed.js`** — depend on data format
6. Backend (1-3) and frontend (5-6) can parallelize once data format is settled

## Verification
- Run `python scripts/fetch_nowigetit.py` locally → confirm `_data/nowigetit-posts.yml` has correct format
- Verify YAML matches expected schema (title, source, url, date, excerpt, image)
- Run `bundle exec jekyll serve` locally → confirm Now I Get It! DevLog posts appear in combined feed
- Verify branded badge renders correctly: black background, gold text, lightbulb icon, correct size
- Posts should render without thumbnails (text-only card format)
- Confirm posts sort correctly by date alongside other sources
- Test GitHub Actions workflow via manual `workflow_dispatch`
- Verify Jekyll deploy chains via `workflow_run`
