#!/usr/bin/env python3
"""
Fetch recent tweets from the X API and save to _data/twitter-posts.yml
Requires TWITTER_BEARER_TOKEN environment variable

Cost model (X pay-per-use, post-Feb-2026 pricing):
  - reading posts:        $0.005 per post returned
  - reading user objects: $0.010 per user returned

Two things keep the bill down, both load-bearing -- do not "simplify" either:

1. The user-object lookup is cached (see resolve_user_id) so it is billed once
   ever, not once per run. A per-run username lookup would add $0.30/month at
   daily cadence for an ID that never changes.

2. Requests are bounded by since_id (see newest_known_tweet_id), so we are
   billed for genuinely new posts rather than re-reading the same recent five
   every day. A quiet day returns zero posts and costs nothing.

Worst case is MAX_TWEETS x $0.005 = $0.125 per run ($3.75/month if every
single day hit the cap); realistic cost at a few posts a week is under
$0.10/month. Without since_id it would be a flat $0.75/month.
"""

import os
import sys
import requests
import yaml
import re
from datetime import datetime

# Configuration
TWITTER_USERNAME = "jbdamask"
# Ceiling on posts returned per run. This is a cost guard, not a target: with
# since_id set we normally get far fewer. It only binds if you post more than
# MAX_TWEETS times between runs. 5 is the API's minimum accepted value.
MAX_TWEETS = 25
# Used only on a cold start (no existing YAML to derive since_id from), to
# avoid a first run that bills for a large backfill.
COLD_START_TWEETS = 5
# Maximum tweets to keep in history (LIFO -- keep newest, drop oldest).
# This is a page-weight limit, not just a file-size one: index.html and
# _includes/sidebar/twitter-feed.html each loop over EVERY entry and emit a
# hidden <div> per post, so this number lands directly in the HTML of every
# page. Trimming here does not touch anything on X, only the site's copy.
MAX_HISTORICAL_TWEETS = 150
OUTPUT_FILE = "_data/twitter-posts.yml"
USER_ID_CACHE = ".twitter-user-id"

# Transient / billing conditions. These mean "no data this run", not "broken
# config", so we skip the update and exit 0 rather than reddening the workflow
# every single day. 402 in particular is a depleted prepaid credit balance,
# which persists until the account is topped up.
SOFT_FAIL_STATUSES = {402, 429, 500, 502, 503, 504}


class SoftFail(Exception):
    """A condition that should skip this run without failing the workflow."""


def warn(message):
    """Emit a GitHub Actions warning annotation (visible without a red run)."""
    print(f"::warning::{message}")


def api_get(bearer_token, url, params=None):
    """GET the X API, mapping transient/billing errors to SoftFail."""
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {bearer_token}"},
        params=params,
        timeout=30,
    )

    if response.status_code == 200:
        return response.json()

    detail = response.text.strip()

    if response.status_code == 402:
        raise SoftFail(
            "X API returned 402 (credits depleted). The prepaid balance is "
            "empty -- top it up at https://console.x.com to resume syncing. "
            f"Response: {detail}"
        )

    if response.status_code == 429:
        raise SoftFail(f"X API rate limit (429); will retry next run. {detail}")

    if response.status_code in SOFT_FAIL_STATUSES:
        raise SoftFail(f"X API transient error {response.status_code}. {detail}")

    # 401/403/404 and friends are genuine misconfiguration -- fail loudly.
    print(f"Error: X API returned {response.status_code}")
    print(detail)
    sys.exit(1)


def resolve_user_id(bearer_token, username):
    """Resolve the numeric user ID, hitting the billed lookup at most once.

    Order: TWITTER_USER_ID env var -> on-disk cache -> API lookup (then cached).
    """
    from_env = os.environ.get("TWITTER_USER_ID", "").strip()
    if from_env:
        print(f"User ID {from_env} (from TWITTER_USER_ID env var)")
        return from_env

    if os.path.exists(USER_ID_CACHE):
        try:
            with open(USER_ID_CACHE) as f:
                cached = f.read().strip()
            if cached:
                print(f"User ID {cached} (cached, no billed lookup)")
                return cached
        except OSError as e:
            print(f"Warning: could not read {USER_ID_CACHE}: {e}")

    print(f"No cached user ID; performing one-time billed lookup for @{username}...")
    data = api_get(
        bearer_token, f"https://api.twitter.com/2/users/by/username/{username}"
    )
    user_id = data["data"]["id"]

    try:
        with open(USER_ID_CACHE, "w") as f:
            f.write(user_id + "\n")
        print(f"Cached user ID {user_id} to {USER_ID_CACHE}")
    except OSError as e:
        warn(f"Could not cache user ID to {USER_ID_CACHE}: {e}")

    return user_id


def newest_known_tweet_id(existing_posts):
    """Highest tweet ID already stored, for use as since_id.

    Tweet IDs are monotonically increasing snowflakes, so the numeric max is
    the most recent post we've already paid for. Returns None if we can't
    determine one (cold start), in which case the caller backfills a little.
    """
    ids = []
    for post in existing_posts:
        m = re.search(r'/status/(\d+)', post.get('url', ''))
        if m:
            ids.append(int(m.group(1)))
    return str(max(ids)) if ids else None


def fetch_tweets(bearer_token, user_id, since_id=None):
    """Fetch tweets newer than since_id from X API v2."""
    params = {
        "tweet.fields": "created_at,text,entities",
        "exclude": "retweets,replies",  # Only original tweets
    }

    if since_id:
        params["since_id"] = since_id
        params["max_results"] = MAX_TWEETS
        print(f"Requesting posts newer than {since_id} (cap {MAX_TWEETS})")
    else:
        params["max_results"] = COLD_START_TWEETS
        print(f"Cold start: no known tweet IDs, fetching {COLD_START_TWEETS} recent posts")

    return api_get(
        bearer_token, f"https://api.twitter.com/2/users/{user_id}/tweets", params=params
    )


def parse_created_at(value):
    """Parse the API timestamp, tolerating presence or absence of milliseconds."""
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized created_at format: {value!r}")


def strip_urls(text):
    """Remove URLs from tweet text"""
    # Remove URLs (http/https)
    text = re.sub(r'https?://\S+', '', text)
    # Remove trailing/leading whitespace and collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_image_url(tweet):
    """Extract first image URL from tweet entities if available"""
    if 'entities' in tweet and 'urls' in tweet['entities']:
        for url_entity in tweet['entities']['urls']:
            if 'images' in url_entity:
                return url_entity['images'][0]['url']
    return ""

def tweets_to_yaml(tweets_data):
    """Convert tweets to YAML format matching external-posts.yml structure"""
    posts = []

    if 'data' not in tweets_data:
        print("No tweets found")
        return posts

    for tweet in tweets_data['data']:
        # Parse date
        created_at = parse_created_at(tweet['created_at'])

        # Get tweet text and strip URLs
        text = strip_urls(tweet['text'])
        excerpt = text[:200] + "..." if len(text) > 200 else text

        # Build tweet URL
        tweet_url = f"https://twitter.com/{TWITTER_USERNAME}/status/{tweet['id']}"

        # Extract image if available
        image = extract_image_url(tweet)

        post = {
            'title': text[:100] + "..." if len(text) > 100 else text,
            'source': 'twitter',
            'url': tweet_url,
            'date': created_at.strftime("%Y-%m-%d"),  # Use date format like Substack
            'excerpt': excerpt,
            'image': image
        }

        posts.append(post)

    return posts

def sort_key(post):
    """Newest first. Tie-break on tweet ID because `date` is day-granular and
    several posts a day is normal -- without this, same-day ordering is
    whatever dict iteration happened to produce."""
    m = re.search(r'/status/(\d+)', post.get('url', ''))
    return (post.get('date', ''), int(m.group(1)) if m else 0)


def trim(posts):
    """Sort newest-first and enforce MAX_HISTORICAL_TWEETS (LIFO)."""
    ordered = sorted(posts, key=sort_key, reverse=True)
    if len(ordered) > MAX_HISTORICAL_TWEETS:
        dropped = len(ordered) - MAX_HISTORICAL_TWEETS
        ordered = ordered[:MAX_HISTORICAL_TWEETS]
        print(f"Trimmed {dropped} oldest tweets from the site's copy "
              f"(keeping {MAX_HISTORICAL_TWEETS} most recent). "
              "Nothing is removed from X itself.")
    return ordered


def write_posts(posts, new_count):
    """Write the feed file."""
    with open(OUTPUT_FILE, 'w') as f:
        f.write("# Twitter posts - automatically generated by fetch_twitter.py\n")
        f.write("# Fetches latest tweets and merges with existing posts\n")
        f.write(f"# Keeps max {MAX_HISTORICAL_TWEETS} most recent tweets (LIFO)\n\n")
        yaml.dump(posts, f, default_flow_style=False, sort_keys=False,
                  allow_unicode=True)
    print(f"✓ Wrote {len(posts)} posts to {OUTPUT_FILE} "
          f"({new_count} from API, {len(posts) - new_count} preserved)")


def main():
    # Get bearer token from environment
    bearer_token = os.environ.get('TWITTER_BEARER_TOKEN')

    if not bearer_token:
        print("Error: TWITTER_BEARER_TOKEN environment variable not set")
        sys.exit(1)

    print(f"Fetching tweets for @{TWITTER_USERNAME}...")

    # Ensure _data directory exists
    os.makedirs('_data', exist_ok=True)

    # Load existing posts first: they preserve history (the API only returns
    # recent tweets) AND they tell us the since_id that bounds what we pay for.
    existing_posts = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                existing_posts = yaml.safe_load(f) or []
            print(f"Loaded {len(existing_posts)} existing posts")
        except Exception as e:
            # Do not fall through to a cold-start backfill on a transient read
            # error -- that would silently re-bill for tweets we already have.
            warn(f"Could not load existing posts ({e}); aborting rather than risk "
                 "overwriting history with a partial fetch.")
            sys.exit(1)

    since_id = newest_known_tweet_id(existing_posts)

    try:
        user_id = resolve_user_id(bearer_token, TWITTER_USERNAME)
        tweets_data = fetch_tweets(bearer_token, user_id, since_id)
    except SoftFail as e:
        warn(str(e))
        print("Skipping update; existing twitter-posts.yml left untouched.")
        sys.exit(0)

    fetched = len(tweets_data.get('data', []))
    print(f"Fetched {fetched} new tweets (billed ~${fetched * 0.005:.3f})")

    # The API returns the *newest* posts up to the cap. If we hit the cap there
    # may be older unseen posts below it -- and because since_id advances to the
    # newest fetched, they will never be picked up by a later run. Say so
    # loudly rather than losing them silently.
    applied_cap = MAX_TWEETS if since_id else COLD_START_TWEETS
    if fetched >= applied_cap:
        warn(
            f"Hit the {applied_cap}-post cap this run. Older posts made since "
            "the last run may have been skipped, and will NOT be picked up "
            "later (since_id advances past them). Raise MAX_TWEETS and re-run "
            "manually if posts are missing."
        )

    if fetched == 0:
        # Still enforce retention: otherwise lowering MAX_HISTORICAL_TWEETS has
        # no effect until the next new post, which could be weeks away.
        if len(existing_posts) > MAX_HISTORICAL_TWEETS:
            print(f"Nothing new, but {len(existing_posts)} stored posts exceed the "
                  f"{MAX_HISTORICAL_TWEETS} limit; trimming.")
            write_posts(trim(existing_posts), new_count=0)
        else:
            print("Nothing new since last run; leaving twitter-posts.yml unchanged.")
        sys.exit(0)

    # Convert to YAML format
    new_posts = tweets_to_yaml(tweets_data)

    # Merge posts: keep existing posts and update/add new ones
    # Create a dictionary of existing posts by URL for fast lookup
    existing_by_url = {post['url']: post for post in existing_posts}

    # Update existing posts or add new ones
    for new_post in new_posts:
        existing_by_url[new_post['url']] = new_post

    # Convert back to list and sort by date (newest first)
    all_posts = list(existing_by_url.values())

    write_posts(trim(all_posts), new_count=len(new_posts))

if __name__ == '__main__':
    main()
