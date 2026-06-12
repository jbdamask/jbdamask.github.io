# Adding HTML and MHTML Pages

## Quick Start

### Adding a Complete, Self-Contained HTML File (As a Blog Post)

**Use this when** you already have a finished HTML document — one that
carries its own `<!DOCTYPE html>`, `<head>`, inline `<style>`, `<body>`,
and any scripts — and you just want it to appear in the timeline. (This
is the path for hand-authored or app-exported pages that are *already*
plain `.html`, not `.mhtml`.)

The helper script copies the file into `_posts/` with the right
`YYYY-MM-DD-slug.html` name and prepends Jekyll front matter using
`layout: app` (full-width, site header, no sidebars). It does **not**
modify your HTML.

```bash
# Title auto-derived from filename, date = today, excerpt = first paragraph
python scripts/add_html_post.py ~/Downloads/my-page.html

# Override any of them
python scripts/add_html_post.py ~/Downloads/my-page.html \
  --title "A Random Walk Through Gas Town" \
  --date 2026-06-12 \
  --excerpt "One-line summary shown on the post card."
```

Then build, commit, and push:

```bash
bundle exec jekyll build      # verify it renders
git add _posts/2026-06-12-a-random-walk-through-gas-town.html
git commit -m "Add post: A Random Walk Through Gas Town"
git push
```

**How it renders:** the file ends up with front matter on top, followed
by your untouched HTML document. The `app` layout wraps it in the site
header and a full-width container. A self-contained document nested this
way renders fine (the browser collapses the inner `<html>/<body>` tags);
your inline `<style>` still applies, and because your `body { ... }`
rules come later in the document they win the cascade over the layout's
defaults. First example of this pattern in the repo:
`_posts/2025-11-25-claude-code-complete-prompts.html`.

If you'd rather not use the script, do it by hand: prepend this block to
the top of your HTML file and save it into `_posts/` as
`YYYY-MM-DD-slug.html`:

```yaml
---
layout: app
title: "Your Title"
date: 2026-06-12
excerpt: "One-line summary for the post card."
---
```

### Adding MHTML Pages (From Your Apps)

**The easiest way** - Use the automated conversion script:

```bash
# Basic usage (auto-generates title from filename)
python scripts/convert_mhtml.py ~/Downloads/my-app-output.mhtml

# With custom title
python scripts/convert_mhtml.py ~/Downloads/my-app-output.mhtml --title "My App Results"

# With custom date
python scripts/convert_mhtml.py ~/Downloads/my-app-output.mhtml --title "My App Results" --date 2025-11-20
```

The script will:
- Convert MHTML to HTML
- Auto-generate Jekyll front matter (title, date, excerpt)
- Extract a text preview for the post card
- Save to `_posts/YYYY-MM-DD-title.html`
- Use full-width app layout (no sidebars)
- Show you the git commands to run next

Then just commit and push:
```bash
git add _posts/2025-11-24-my-app-results.html
git commit -m "Add post: My App Results"
git push
```

Your app page will appear in your timeline as a card with the BLOG badge!

### Adding Regular HTML Pages

For static HTML pages that don't need to be in the timeline:

**Option 1: With Site Header/Footer**
```html
---
layout: single
title: "My Page"
permalink: /my-page/
---

<h2>Your Content</h2>
<p>Any HTML here...</p>
```

**Option 2: Full-Width (Like App Pages)**
```html
---
layout: app
title: "My Full-Width Page"
---

<h2>Your Content</h2>
<p>Uses entire viewport width...</p>
```

**Option 3: Standalone (No Header)**
Create `.html` file without front matter - served as-is.

## Script Options

The `convert_mhtml.py` script supports:

```bash
# Show help
python scripts/convert_mhtml.py --help

# Examples
python scripts/convert_mhtml.py input.mhtml --title "Custom Title"
python scripts/convert_mhtml.py input.mhtml --date 2025-11-20
python scripts/convert_mhtml.py input.mhtml --output _posts/2025-11-24-custom-name.html
```

## How It Works

### MHTML Conversion Process

1. **Parse MHTML** - Splits file by MIME boundaries
2. **Extract HTML & CSS** - Finds `Content-Type: text/html` and `text/css` sections
3. **Decode quoted-printable** - Converts `=3D` → `=`, `=E2=96=BA` → `►`, etc.
4. **Embed CSS inline** - Inserts `<style>` tag in `<head>`
5. **Add front matter** - Creates Jekyll metadata (title, date, excerpt)
6. **Generate filename** - Creates `_posts/YYYY-MM-DD-slug.html`

### What You Get

- **Full-width layout** - App content uses entire viewport
- **Matching header** - Site title and navigation at top
- **Post card** - Appears in timeline with excerpt
- **Self-contained** - All CSS and assets embedded
- **Clickable** - Opens full interactive app page

## Directory Structure

```
/
├── _posts/
│   ├── 2025-11-24-my-app-output.html    ← MHTML conversions go here
│   └── 2025-11-24-blog-post.md          ← Regular blog posts
├── tools/
│   ├── calculator.html                   ← Standalone tools
│   └── calculator.md                     ← Tool documentation
├── example-page.html                     ← Static pages
└── scripts/
    └── convert_mhtml.py                  ← Conversion script
```

## Tips

1. **For app outputs**: Always use the MHTML conversion script
2. **For static tools**: Put in `tools/` directory (see README.md)
3. **For blog posts**: Use markdown in `_posts/` (see example)
4. **Test locally**: `bundle exec jekyll serve` before pushing
5. **Check the card**: Excerpt is auto-generated from first 200 chars

## Troubleshooting

**"No HTML content found in MHTML file"**
- Make sure you saved as "Webpage, Single File (.mhtml)" in your browser
- Try re-saving the page

**"Layout 'app' not found"**
- Make sure `_layouts/app.html` exists in your repo
- Pull latest changes: `git pull`

**Post doesn't appear in timeline**
- Check filename format: `YYYY-MM-DD-title.html`
- Verify it's in `_posts/` directory
- Check front matter has `layout: app`, `title`, `date`, `excerpt`
