#!/usr/bin/env python3
"""
Add a complete, self-contained HTML file as a blog post.

Use this when you already have a finished HTML document (its own
<!DOCTYPE html>, <head>, <style>, <body>, scripts -- everything inline)
and just want it to show up in the timeline. Unlike convert_mhtml.py,
this does NOT transform the HTML; it only prepends Jekyll front matter
and copies the file into _posts/ with the correct YYYY-MM-DD-slug.html
name so it renders under `layout: app` (full-width, site header, no
sidebars).

Usage:
    python scripts/add_html_post.py ~/Downloads/my-page.html
    python scripts/add_html_post.py ~/Downloads/my-page.html --title "My Page"
    python scripts/add_html_post.py input.html --title "My Page" --date 2026-06-12 \
        --excerpt "One-line summary for the post card."
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import make_social_card

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "_posts"


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def title_from_filename(path):
    stem = Path(path).stem
    return stem.replace("-", " ").replace("_", " ").title()


def extract_excerpt(html):
    """Pull the first chunk of visible paragraph text for the post card."""
    match = re.search(r"<p[^>]*>(.*?)</p>", html, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    text = re.sub(r"<[^>]+>", "", match.group(1))
    text = re.sub(r"\s+", " ", text).strip()
    return (text[:197] + "...") if len(text) > 200 else text


def escape_yaml(value):
    return value.replace('"', '\\"')


def main():
    parser = argparse.ArgumentParser(
        description="Add a self-contained HTML file as a Jekyll blog post."
    )
    parser.add_argument("input", help="Path to the source .html file")
    parser.add_argument("--title", help="Post title (default: from filename)")
    parser.add_argument(
        "--date", help="Post date YYYY-MM-DD (default: today)"
    )
    parser.add_argument(
        "--excerpt", help="Post-card excerpt (default: first paragraph of the HTML)"
    )
    parser.add_argument(
        "--output", help="Explicit output path (default: _posts/DATE-slug.html)"
    )
    args = parser.parse_args()

    src = Path(args.input).expanduser()
    if not src.exists():
        sys.exit(f"Error: input file not found: {src}")

    html = src.read_text(encoding="utf-8", errors="ignore")

    if html.lstrip().startswith("---"):
        sys.exit(
            "Error: this file already starts with front matter. It looks like it "
            "was already processed -- copy it into _posts/ directly instead."
        )

    title = args.title or title_from_filename(src)
    date = args.date or datetime.now().strftime("%Y-%m-%d")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        sys.exit(f"Error: --date must be YYYY-MM-DD, got: {date}")

    excerpt = args.excerpt if args.excerpt is not None else extract_excerpt(html)

    if args.output:
        dest = Path(args.output)
        if not dest.is_absolute():
            dest = REPO_ROOT / dest
    else:
        dest = POSTS_DIR / f"{date}-{slugify(title)}.html"

    # Every direct post gets a companion social card automatically. This is
    # required for share previews and must not depend on a human remembering.
    slug = dest.stem
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug)
    image_line = ""
    card_msg = None
    try:
        image_path = make_social_card.generate_card(slug, title, excerpt)
        image_line = f"image: {image_path}\n"
        card_msg = f"  card:    {image_path}"
    except Exception as exc:  # noqa: BLE001 -- never block post creation on card render
        card_msg = (
            f"  card:    FAILED ({exc})\n"
            f"           Run: python scripts/make_social_card.py --post {dest.relative_to(REPO_ROOT)}"
        )

    front_matter = (
        "---\n"
        "layout: app\n"
        f'title: "{escape_yaml(title)}"\n'
        f"date: {date}\n"
        f'excerpt: "{escape_yaml(excerpt)}"\n'
        f"{image_line}"
        "---\n\n"
    )

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(front_matter + html, encoding="utf-8")

    rel = dest.relative_to(REPO_ROOT)
    print(f"Created {rel}")
    print(f"  title:   {title}")
    print(f"  date:    {date}")
    print(f"  excerpt: {excerpt or '(none)'}")
    print(card_msg)
    print()
    print("Next steps:")
    print("  bundle exec jekyll build   # verify it renders")
    print(f"  git add {rel}")
    print(f'  git commit -m "Add post: {title}"')
    print("  git push")


if __name__ == "__main__":
    main()
