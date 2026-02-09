# Substack RSS Feed Fix — Specification

**GitHub Issue:** [#1 — Pulling from Substack is broken](https://github.com/jbdamask/jbdamask.github.io/issues/1)
**Date:** 2026-02-09

---

## 1. The Problem

The GitHub Actions workflow `fetch-substack.yml` runs hourly to fetch posts from `https://johndamask.substack.com/feed` and update `_data/substack-posts.yml`. Since approximately **2025-11-25** (the date of the last successful auto-update commit), Substack has been returning **HTTP 403 Forbidden** to every request made from GitHub Actions runners.

The workflow still reports **success** because the Python script (`scripts/fetch_substack.py`) catches the 403, prints an error to stdout, and exits with code 0. The "Commit and push" step then sees no changes and skips. The site continues to display the 20 stale posts that were last fetched on 2025-11-25.

**Evidence from workflow logs:**
```
Fetching from https://johndamask.substack.com/feed...
Error fetching Substack feed: 403
No posts fetched. Keeping existing file if it exists.
```

## 2. Root Cause

Substack blocks HTTP requests originating from GitHub Actions runner IP ranges. This is a known issue affecting CI/CD pipelines across multiple platforms (GitHub Actions, Netlify build runners, etc.).

Key findings:
- The RSS feed URL works fine from local machines with **any** User-Agent (curl default, `python-requests`, browser-like)
- The feed returns **403** specifically from GitHub Actions infrastructure
- This is an IP-based block, not a User-Agent block — Substack (or its CDN/WAF, likely Cloudflare) maintains a blocklist of cloud/datacenter IP ranges commonly used by CI runners
- This is a well-documented pattern across the community (see Sources below)

The `requests.get()` call in `fetch_substack.py` (line 31) sends a bare request with no special headers, but even adding a browser-like User-Agent would not help since the block is IP-based.

## 3. The Fix

### Recommended approach: CloudFlare Worker proxy

The codebase already uses a CloudFlare Worker pattern for the audio transcriber tool (`openai-proxy.jbdamask.workers.dev`). A similar lightweight worker can proxy the Substack RSS feed request, since CloudFlare Worker egress IPs are not blocked by Substack.

**Changes required:**

#### A. Create a CloudFlare Worker (new)
A minimal worker that:
- Accepts a request to a known path (e.g., `GET /substack-feed`)
- Fetches `https://johndamask.substack.com/feed` server-side
- Returns the RSS XML response
- Optionally restricts the allowed origin/referer to prevent abuse

#### B. Update `scripts/fetch_substack.py`
- Change `SUBSTACK_FEED` URL from the direct Substack URL to the CloudFlare Worker URL
- No other logic changes needed — the XML response format is unchanged

#### C. Update `scripts/fetch_substack.py` error handling
- Exit with a non-zero code when the feed fetch fails, so the workflow properly reports failure
- This makes the silent-success bug visible in GitHub Actions

#### D. No workflow changes needed
- `fetch-substack.yml` requires no modifications

### Alternative approaches considered

| Approach | Pros | Cons |
|----------|------|------|
| **CloudFlare Worker proxy** (recommended) | Already a pattern in this codebase; free tier; reliable; fast | Requires CloudFlare account setup (already exists) |
| **Run fetch locally on a schedule** | No proxy needed | Requires local machine to be running; not automated |
| **Use a generic CORS/RSS proxy service** | No infrastructure to manage | Third-party dependency; rate limits; reliability concerns |
| **Self-hosted proxy on another cloud** | Full control | Over-engineered for this use case |
| **Substack API with auth token** | Direct access | Substack has no official public API; fragile |

---

**Sources:**
- [Netlify Forums — RSS feed via GitHub results in 403](https://answers.netlify.com/t/loading-rss-feed-via-github-results-in-a-403-error/109625)
- [RSS-Bridge — Substack bridge documentation](https://rss-bridge.github.io/rss-bridge/Bridge_Specific/Substack.html)
- [Hacker News discussion on RSS feed access challenges](https://news.ycombinator.com/item?id=43245088)
