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
- `_config.yml` - Jekyll configuration
- `aboutme.md` - About page
- `index.html` - Homepage
- `tools/` - Standalone HTML tools (automatically discovered)
- `tools.md` - Tools landing page

## Adding Tools

The site includes an automatic tool discovery system. To add a new tool:

1. Create a standalone HTML file (e.g., `my-awesome-tool.html`)
2. Copy it to the `tools/` directory
3. Commit and push to GitHub
4. The tool will automatically appear on the `/tools/` page!

The file name will be converted to a display name (e.g., `my-awesome-tool.html` → "My Awesome Tool").

**Optional:** Add a description meta tag in your HTML for better documentation:
```html
<meta name="tool-description" content="Brief description of what this tool does">
```

## Theme Documentation

For theme customization options, see the [Minimal Mistakes documentation](https://mmistakes.github.io/minimal-mistakes/docs/quick-start-guide/).
