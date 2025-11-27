#!/usr/bin/env python3
"""
Fetch recent tweets from Twitter API and save to _data/twitter-posts.yml
Requires TWITTER_BEARER_TOKEN environment variable
"""

import os
import sys
import requests
import yaml
import re
from datetime import datetime

# Configuration
TWITTER_USERNAME = "jbdamask"
MAX_TWEETS = 5  # Keep it low for Free tier (max 10)
MAX_HISTORICAL_TWEETS = 250  # Maximum tweets to keep in history (LIFO)
OUTPUT_FILE = "_data/twitter-posts.yml"

def get_user_id(bearer_token, username):
    """Get Twitter user ID from username"""
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    headers = {"Authorization": f"Bearer {bearer_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error getting user ID: {response.status_code}")
        print(response.text)
        sys.exit(1)

    data = response.json()
    return data['data']['id']

def fetch_tweets(bearer_token, user_id, max_results=10):
    """Fetch recent tweets from Twitter API v2"""
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"

    headers = {"Authorization": f"Bearer {bearer_token}"}

    params = {
        "max_results": max_results,
        "tweet.fields": "created_at,text,entities",
        "exclude": "retweets,replies"  # Only original tweets
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 429:
        print("Rate limit exceeded (429). This is expected on Twitter Free tier.")
        print("The workflow runs daily, so rate limits will reset before the next run.")
        print("Keeping existing twitter-posts.yml file (if it exists).")
        return None

    if response.status_code != 200:
        print(f"Error fetching tweets: {response.status_code}")
        print(response.text)
        sys.exit(1)

    return response.json()

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
        created_at = datetime.strptime(tweet['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")

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
            'date': created_at.isoformat(),  # Store full timestamp for proper sorting
            'excerpt': excerpt,
            'image': image
        }

        posts.append(post)

    return posts

def main():
    # Get bearer token from environment
    bearer_token = os.environ.get('TWITTER_BEARER_TOKEN')

    if not bearer_token:
        print("Error: TWITTER_BEARER_TOKEN environment variable not set")
        sys.exit(1)

    print(f"Fetching tweets for @{TWITTER_USERNAME}...")

    # Get user ID
    user_id = get_user_id(bearer_token, TWITTER_USERNAME)
    print(f"User ID: {user_id}")

    # Fetch tweets
    tweets_data = fetch_tweets(bearer_token, user_id, MAX_TWEETS)

    # If rate limited, exit gracefully without updating the file
    if tweets_data is None:
        print("Skipping update due to rate limit.")
        sys.exit(0)

    print(f"Fetched {len(tweets_data.get('data', []))} tweets")

    # Convert to YAML format
    new_posts = tweets_to_yaml(tweets_data)

    # Ensure _data directory exists
    os.makedirs('_data', exist_ok=True)

    # Load existing posts to preserve history (API only returns recent tweets)
    existing_posts = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                existing_posts = yaml.safe_load(f) or []
            print(f"Loaded {len(existing_posts)} existing posts")
        except Exception as e:
            print(f"Warning: Could not load existing posts: {e}")

    # Merge posts: keep existing posts and update/add new ones
    # Create a dictionary of existing posts by URL for fast lookup
    existing_by_url = {post['url']: post for post in existing_posts}

    # Update existing posts or add new ones
    for new_post in new_posts:
        existing_by_url[new_post['url']] = new_post

    # Convert back to list and sort by date (newest first)
    all_posts = list(existing_by_url.values())
    all_posts.sort(key=lambda p: p['date'], reverse=True)

    # Limit to MAX_HISTORICAL_TWEETS (LIFO - keep newest, remove oldest)
    original_count = len(all_posts)
    if len(all_posts) > MAX_HISTORICAL_TWEETS:
        all_posts = all_posts[:MAX_HISTORICAL_TWEETS]
        removed_count = original_count - len(all_posts)
        print(f"Trimmed {removed_count} oldest tweets (keeping {MAX_HISTORICAL_TWEETS} most recent)")

    # Write to YAML file
    with open(OUTPUT_FILE, 'w') as f:
        f.write("# Twitter posts - automatically generated by fetch_twitter.py\n")
        f.write("# Fetches latest tweets and merges with existing posts\n")
        f.write(f"# Keeps max {MAX_HISTORICAL_TWEETS} most recent tweets (LIFO)\n\n")
        yaml.dump(all_posts, f, default_flow_style=False, sort_keys=False, allow_unicode=True, default_style="'")

    print(f"✓ Wrote {len(all_posts)} posts to {OUTPUT_FILE} ({len(new_posts)} from API, {len(all_posts) - len(new_posts)} preserved)")

if __name__ == '__main__':
    main()
