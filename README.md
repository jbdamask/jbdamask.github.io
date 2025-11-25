# John Damask's Personal Site

This site uses the [Minimal Mistakes](https://github.com/mmistakes/minimal-mistakes) theme for Jekyll.

## Development

### Local Setup

```bash
bundle install
bundle exec jekyll serve
```

### Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions when changes are pushed to the `main` branch.

## Site Structure

- `_posts/` - Blog posts
- `_data/external-posts.yml` - Manual LinkedIn/Twitter posts
- `_config.yml` - Jekyll configuration
- `aboutme.md` - About page
- `index.html` - Homepage
- `tools/` - Standalone HTML tools (automatically discovered)
- `tools.md` - Tools landing page

## Adding Tools

The site includes an automatic tool discovery system with two workflows:

### Simple Tool (HTML only)

1. Create a standalone HTML file (e.g., `my-tool.html`)
2. Copy it to the `tools/` directory
3. Commit and push
4. Tool appears on `/tools/` with a "Launch Tool →" button

### Tool with Documentation (HTML + Markdown)

For tools that need documentation, create companion markdown files:

1. Create your tool: `pretty-markdown.html`
2. Create matching docs: `pretty-markdown.md` with front matter:
   ```yaml
   ---
   title: Pretty Markdown
   tool_url: /tools/pretty-markdown.html
   excerpt: Brief description
   permalink: /tools/pretty-markdown/
   ---

   Your documentation here...
   ```
3. Copy both to `tools/`
4. Tool appears with two buttons: "Learn More" and "Launch →"

**The system automatically detects companion files** by matching filenames (e.g., `tool.html` + `tool.md`).

File names are auto-converted to display names: `my-awesome-tool.html` → "My Awesome Tool"

## Adding Blog Posts

### Markdown Posts (Recommended)

Create a markdown file in `_posts/` with the naming pattern `YYYY-MM-DD-your-post-title.md`:

```markdown
---
layout: single
title: "Your Post Title"
date: 2025-11-25
excerpt: "A brief description that appears in the timeline"
categories:
  - Blog
tags:
  - your-tags
---

Your markdown content here...

## Heading

Content with **bold** and *italic* text.

- Lists work great
- Another item

```code blocks too```
```

The post will automatically appear in your timeline with proper styling.

### HTML Posts (For App Outputs)

For interactive app outputs saved as MHTML, use the conversion script:

```bash
python scripts/convert_mhtml.py ~/Downloads/my-app.mhtml --title "My App Results"
```

See `ADDING_HTML_PAGES.md` for full details.

## Adding External Posts (LinkedIn, Twitter, etc.)

Since LinkedIn and Twitter don't provide free API access, you can manually add posts to `_data/external-posts.yml`:

```yaml
- title: "Your post title"
  source: linkedin  # or twitter
  url: https://www.linkedin.com/posts/...
  date: 2024-11-23
  excerpt: "Brief description of the post..."
  image: "/assets/images/post-image.png"  # optional
```

These posts will automatically appear in your unified feed alongside Substack and blog posts, sorted by date.

## Theme Documentation

For theme customization options, see the [Minimal Mistakes documentation](https://mmistakes.github.io/minimal-mistakes/docs/quick-start-guide/).
