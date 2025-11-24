# Twitter Integration Setup

This site uses GitHub Actions to automatically fetch your Twitter posts and display them alongside your blog posts, Substack articles, and LinkedIn posts.

## Prerequisites

1. A Twitter API Bearer Token (you mentioned you have this)
2. Access to your GitHub repository settings

## Setup Instructions

### Step 1: Add Twitter Bearer Token to GitHub Secrets

1. Go to your GitHub repository: https://github.com/jbdamask/jbdamask.github.io
2. Click on **Settings** (top navigation)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click the **New repository secret** button
5. Add your secret:
   - **Name**: `TWITTER_BEARER_TOKEN`
   - **Value**: Paste your Twitter API Bearer Token
6. Click **Add secret**

### Step 2: Manually Trigger the Workflow (First Run)

Since the workflow is scheduled to run daily at 6 AM UTC, you can trigger it manually for the first time:

1. Go to the **Actions** tab in your repository
2. Click on **Fetch Twitter Posts** in the left sidebar
3. Click the **Run workflow** button (on the right)
4. Click the green **Run workflow** button in the dropdown
5. Wait for the workflow to complete (usually takes ~30 seconds)

### Step 3: Verify It Works

After the workflow completes:

1. Check if `_data/twitter-posts.yml` was created in your repository
2. Visit your site at https://jbdamask.github.io/posts/
3. You should see your recent tweets displayed with the Twitter badge

## How It Works

### Automated Daily Updates

- The workflow runs automatically every day at 6 AM UTC
- It fetches your 10 most recent tweets (excluding retweets and replies)
- Tweets are saved to `_data/twitter-posts.yml`
- The site rebuilds and displays the updated tweets

### Manual Updates

You can manually trigger the workflow anytime from the Actions tab if you want to update your tweets immediately.

### What Gets Fetched

- **Only your original tweets** (no retweets or replies)
- **Last 10 tweets**
- Tweet text, link, date, and images (if available)

## Files Created

1. `.github/workflows/fetch-twitter.yml` - GitHub Actions workflow
2. `scripts/fetch_twitter.py` - Python script that fetches tweets
3. `_data/twitter-posts.yml` - Generated file with your tweets (auto-created on first run)

## Troubleshooting

### Workflow fails with authentication error

- Check that your `TWITTER_BEARER_TOKEN` secret is set correctly
- Verify your Twitter API key is still valid

### No tweets appear on the site

- Check the Actions tab to see if the workflow ran successfully
- Verify `_data/twitter-posts.yml` exists and has content
- Check browser console for JavaScript errors

### Tweets are outdated

- The workflow runs daily at 6 AM UTC
- Manually trigger it from the Actions tab for immediate updates

## Twitter API Information

The integration uses the Twitter API v2 endpoint:
- Endpoint: `GET /2/users/:id/tweets`
- Required scopes: Read tweets
- Free tier supported (if you have the Bearer Token, it should work)

## Need Help?

If you encounter issues, check:
1. GitHub Actions logs in the Actions tab
2. The `_data/twitter-posts.yml` file to see if tweets were fetched
3. Browser console for JavaScript errors when viewing the site
