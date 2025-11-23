# John Damask's Personal Site

This site uses the [Bulma Clean Theme](https://github.com/chrisrhymes/bulma-clean-theme) for Jekyll.

## Development

### Local Setup

```bash
bundle install
bundle exec jekyll serve
```

Note: If you encounter SSL certificate errors when building locally, this is a system configuration issue and won't affect GitHub Pages deployment.

### Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions when changes are pushed to the `main` branch.

## Site Structure

- `_posts/` - Blog posts
- `_data/navigation.yml` - Navigation menu configuration
- `_config.yml` - Jekyll configuration
- `aboutme.md` - About page
- `blog.html` - Blog archive page
- `index.html` - Homepage

## Theme Documentation

For theme customization options, see the [Bulma Clean Theme documentation](https://www.csrhymes.com/bulma-clean-theme/docs/).
