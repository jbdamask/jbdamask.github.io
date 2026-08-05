# Twitter Integration Setup

This site uses GitHub Actions to fetch posts from X (Twitter) and display them
alongside your blog posts, Substack articles, and LinkedIn posts.

> **The X API is no longer free.** X discontinued the free tier on 2026-02-06
> and moved to prepaid pay-per-use credits. This integration will not run
> without a funded balance. See [Billing](#billing) — it is the single most
> common reason this stops working.

## Prerequisites

1. An X API Bearer Token
2. A funded credit balance at [console.x.com](https://console.x.com)
3. Access to your GitHub repository settings

## Setup Instructions

### Step 1: Add the Bearer Token to GitHub Secrets

1. Go to https://github.com/jbdamask/jbdamask.github.io
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret**
   - **Name**: `TWITTER_BEARER_TOKEN`
   - **Value**: your X API Bearer Token

### Step 2: Trigger the Workflow Manually (First Run)

1. Go to the **Actions** tab
2. Click **Fetch Twitter Posts** in the left sidebar
3. **Run workflow** → **Run workflow**
4. It completes in roughly 30 seconds

### Step 3: Verify

1. Confirm `_data/twitter-posts.yml` was updated
2. Visit https://johndamask.com/posts/
3. Recent posts should appear with the Twitter badge

## How It Works

### Schedule

Runs once daily at **12:17 UTC** (`17 12 * * *`). The offset from the top of
the hour is deliberate — jobs scheduled at `:00` queue behind the rest of
GitHub and can be delayed or dropped entirely.

Cadence is a **cost decision**, not a freshness one. See [Billing](#billing)
before changing it.

### What Gets Fetched

- **Only original posts** — retweets and replies are excluded
- **Only posts newer than what's already stored**, via `since_id`
- Post text (URLs stripped), link, date, and image if available

The script derives `since_id` from the highest post ID already in
`_data/twitter-posts.yml`, so each run pays only for genuinely new posts. A day
with no posts returns nothing and costs nothing. Up to 25 posts are accepted
per run; on a cold start (no existing YAML) it backfills a bounded 5.

History is preserved across runs — the API only returns recent posts, so the
script merges new results into the existing file and keeps the newest 150
(`MAX_HISTORICAL_TWEETS`).

That cap is a **page-weight** limit, not just a file-size one: `index.html` and
`_includes/sidebar/twitter-feed.html` each emit a hidden `<div>` per stored
post, so every entry lands in the HTML of every page. Retention is enforced on
every run, including runs that fetch nothing — so lowering the number takes
effect on the next run rather than waiting for your next post.

Trimming only affects the site's copy. **Nothing is ever deleted from X.**

### Manual Updates

Trigger from the Actions tab anytime. A `concurrency` group prevents a manual
run from racing the scheduled one into the same push.

## Billing

X bills **per resource returned**, not per request:

| Resource | Cost |
|---|---|
| Post read | $0.005 each |
| User object read | $0.010 each |

Two design choices keep this cheap. **Do not undo either one:**

1. **The numeric user ID is cached** in `.twitter-user-id` (committed to the
   repo, overridable via a `TWITTER_USER_ID` env var). The billed username
   lookup happens once, ever. Restoring a per-run lookup adds $0.30/month for
   an ID that never changes.
2. **Requests are bounded by `since_id`.** Without it, every run re-reads the
   same recent posts at full price.

Actual cost:

| Cadence | Cost |
|---|---|
| Daily + `since_id` (current) | **~$0.06–0.10/month** |
| Daily, worst case (25 posts every day) | $3.75/month |
| Hourly, fixed 5-post window | ~$18/month |

That last row is not hypothetical — an hourly schedule is what drained the
credit balance on 2026-03-30 and left the workflow failing for four months.

Set a **spending limit** in the X developer console. The script is bounded, but
a cap protects you from anything else using the same credentials.

## Failure Behavior

The script distinguishes two kinds of failure, on purpose:

| Condition | Behavior |
|---|---|
| `402` credits depleted | Exit 0, `::warning::` annotation, YAML untouched |
| `429` rate limited | Exit 0, warning, retry next run |
| `5xx` upstream error | Exit 0, warning, retry next run |
| `401` / `403` / `404` | **Exit 1** — genuine misconfiguration |

Transient and billing problems do not fail the workflow. This was a deliberate
change: the old script called `sys.exit(1)` on any non-200, which produced
~3,000 consecutive red runs after credits lapsed.

**The tradeoff:** a lapsed balance is now quiet. If the feed stops updating but
Actions is green, **check your credit balance first** — then look for a warning
annotation on the most recent run, which will say exactly what happened.

## Files

| Path | Purpose |
|---|---|
| `.github/workflows/fetch-twitter.yml` | Workflow definition |
| `scripts/fetch_twitter.py` | Fetch + merge script |
| `_data/twitter-posts.yml` | Generated feed data (max 150 posts) |
| `.twitter-user-id` | Cached numeric user ID — avoids a billed lookup per run |

## Troubleshooting

### Feed stopped updating but the workflow is green

Almost certainly depleted credits. Check the balance at
[console.x.com](https://console.x.com), then open the latest run in the Actions
tab and look for a warning annotation. Once funded, the next run resumes on its
own — no code change needed.

### Workflow fails with exit code 1

A `401`/`403` means the token is invalid, revoked, or lacks read scope.
Regenerate it and update the `TWITTER_BEARER_TOKEN` secret.

### Posts appear to be missing

The API returns the **newest** posts up to the 25-per-run cap. If you made more
than 25 posts since the last run, the older ones below the cap are skipped —
and because `since_id` advances to the newest post fetched, **a later run will
not pick them up**. They are skipped permanently.

The script emits a warning annotation whenever it hits the cap, so this is
visible rather than silent. To recover: raise `MAX_TWEETS` in
`scripts/fetch_twitter.py` and trigger a manual run *before* the next scheduled
one advances `since_id` any further. Failing that, remove the offending newer
entries from `_data/twitter-posts.yml` to roll `since_id` back, then re-run.

At daily cadence this requires posting 25+ times in one day, so it is unlikely.

### No posts appear on the site

- Confirm the workflow ran successfully in the Actions tab
- Confirm `_data/twitter-posts.yml` has content
- Confirm the Jekyll deploy ran afterward
- Check the browser console for JavaScript errors

## API Reference

- Endpoint: `GET /2/users/:id/tweets` (X API v2 — current; there is no v3)
- Params used: `since_id`, `max_results`, `tweet.fields`, `exclude`
- Required scope: read posts

### Why not webhooks?

The [X Activity API](https://docs.x.com/x-api/activity/introduction) can push
`post.create` events instead of polling, but it was evaluated and rejected:

- **No cost saving.** Activity events bill $0.005 each — identical to a post
  read. With `since_id` polling already at ~$0.06/month, there is nothing to
  gain.
- **Substantial infrastructure.** X requires a public HTTPS endpoint with no
  port, not behind a firewall, responding 200 within 10 seconds, plus
  HMAC-SHA256 CRC validation every 30 minutes. GitHub Pages cannot receive
  POSTs, so this needs Lambda + API Gateway, OAuth 1.0a credentials, and a
  GitHub write token stored in AWS.
- **Polling is self-healing; webhooks are not.** A dropped event is gone
  permanently — there is no replay. `since_id` simply catches up next run. The
  standard mitigation is a reconciliation poll alongside the webhook, which
  means maintaining both.

The only real gain is latency (seconds vs up to 24 hours), which is worth
approximately nothing for a blog sidebar.
