#!/usr/bin/env python3
"""
Generate a social / Open Graph card (1200x630 PNG) for a blog post.

This is the automated path: callers pass a post's slug, title, and
excerpt and get back a rendered card plus its web path, with no design
work and nothing for a human to remember. `add_html_post.py` and
`convert_mhtml.py` call generate_card() automatically after creating a
post and wire the result into the post's `image:` front matter.

It builds a self-contained, on-brand card (Amroja blue, the site mark,
the post title + excerpt, the canonical domain) and screenshots it with
headless Chrome. Bespoke, hand-designed cards are still welcome -- if a
post already declares `image:`, the --post / --all backfill modes leave
it untouched.

Standalone usage:
    # Render a card from explicit fields
    python scripts/make_social_card.py --slug my-post \
        --title "My Post" --excerpt "One-line summary."

    # Read a post file's front matter, render, and wire in `image:`
    python scripts/make_social_card.py --post _posts/2026-06-15-my-post.html

    # Backfill: ensure every direct post missing `image:` gets a card
    python scripts/make_social_card.py --all
"""

import argparse
import base64
import html as html_lib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CARDS_SRC_DIR = REPO_ROOT / "assets" / "social-cards"
IMAGES_DIR = REPO_ROOT / "assets" / "images"
ICON_PATH = IMAGES_DIR / "amroja-icon.png"
SITE_NAME = "Interested autodidact"
SITE_DOMAIN = "johndamask.com"

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "chrome",
]


def find_chrome():
    for cand in CHROME_CANDIDATES:
        if "/" in cand:
            if Path(cand).exists():
                return cand
        else:
            found = shutil.which(cand)
            if found:
                return found
    return None


def _icon_data_uri():
    if not ICON_PATH.exists():
        return None
    b64 = base64.b64encode(ICON_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _title_font_px(title):
    """Scale the headline down as the title grows so it never overflows."""
    n = len(title)
    if n <= 28:
        return 92
    if n <= 42:
        return 76
    if n <= 60:
        return 62
    if n <= 80:
        return 52
    return 44


def build_card_html(title, excerpt):
    icon = _icon_data_uri()
    icon_img = (
        f'<img class="mark" src="{icon}" alt="">' if icon else ""
    )
    safe_title = html_lib.escape(title)
    safe_excerpt = html_lib.escape(excerpt or "")
    excerpt_block = (
        f'<p class="excerpt">{safe_excerpt}</p>' if safe_excerpt else ""
    )
    title_px = _title_font_px(title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<!-- AUTO-GENERATED social card source. Regenerate with scripts/make_social_card.py;
     hand edits here are overwritten the next time the card is rebuilt. -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root{{
    --blue:#1b5e9c;
    --ink:#1f2630;
    --ink-soft:#55606e;
    --paper:#f7f3ea;
    --line:#e0d8c6;
  }}
  *{{box-sizing:border-box;margin:0;padding:0;}}
  html,body{{width:1200px;height:630px;}}
  body{{
    font-family:'Inter',-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
    color:var(--ink);
    background:var(--paper);
    background-image:
      radial-gradient(ellipse 70% 60% at 88% 6%, rgba(27,94,156,0.10), transparent 60%),
      radial-gradient(ellipse 60% 50% at 4% 96%, rgba(27,94,156,0.07), transparent 60%);
    overflow:hidden;
  }}
  .card{{
    width:1200px;height:630px;
    padding:72px 80px;
    display:flex;flex-direction:column;
    border:3px solid var(--ink);
    border-radius:20px;
    position:relative;
  }}
  .bar{{
    position:absolute;left:0;top:0;bottom:0;width:14px;
    background:var(--blue);
    border-radius:18px 0 0 18px;
  }}
  .kicker{{
    display:flex;align-items:center;gap:16px;
    font-weight:600;font-size:26px;letter-spacing:.04em;
    text-transform:uppercase;color:var(--blue);
  }}
  .mark{{width:46px;height:46px;object-fit:contain;}}
  h1{{
    font-family:'Fraunces','Georgia',serif;
    font-weight:600;
    font-size:{title_px}px;
    line-height:1.04;
    margin-top:34px;
    color:var(--ink);
    letter-spacing:-0.01em;
  }}
  .excerpt{{
    font-size:32px;line-height:1.42;
    color:var(--ink-soft);
    margin-top:30px;
    max-width:1000px;
    display:-webkit-box;
    -webkit-line-clamp:3;
    -webkit-box-orient:vertical;
    overflow:hidden;
  }}
  .footer{{
    margin-top:auto;
    display:flex;align-items:center;justify-content:space-between;
    padding-top:28px;
    border-top:2px solid var(--line);
    font-size:27px;color:var(--ink-soft);
  }}
  .footer .site{{font-weight:600;color:var(--ink);}}
  .footer .domain{{color:var(--blue);font-weight:600;}}
</style>
</head>
<body>
  <div class="card">
    <div class="bar"></div>
    <div class="kicker">{icon_img}<span>{html_lib.escape(SITE_NAME)}</span></div>
    <h1>{safe_title}</h1>
    {excerpt_block}
    <div class="footer">
      <span class="site">John Damask</span>
      <span class="domain">{SITE_DOMAIN}</span>
    </div>
  </div>
</body>
</html>
"""


def render_png(card_html, out_png):
    chrome = find_chrome()
    if not chrome:
        raise RuntimeError(
            "No Chrome/Chromium binary found to render the card. "
            "Install Google Chrome or set one of: " + ", ".join(CHROME_CANDIDATES)
        )
    out_png.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", suffix=".html", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(card_html)
        tmp_path = Path(tmp.name)
    try:
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                "--window-size=1200,630",
                f"--screenshot={out_png}",
                tmp_path.as_uri(),
                "--virtual-time-budget=4000",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    finally:
        tmp_path.unlink(missing_ok=True)
    if not out_png.exists():
        raise RuntimeError(f"Chrome did not produce {out_png}")


def generate_card(slug, title, excerpt, *, repo_root=REPO_ROOT, save_source=True):
    """Build and render a card. Returns the site-absolute image path
    (e.g. /assets/images/<slug>-card.png) or raises on failure."""
    card_html = build_card_html(title, excerpt)
    if save_source:
        CARDS_SRC_DIR.mkdir(parents=True, exist_ok=True)
        (CARDS_SRC_DIR / f"{slug}.html").write_text(card_html, encoding="utf-8")
    out_png = IMAGES_DIR / f"{slug}-card.png"
    render_png(card_html, out_png)
    return f"/assets/images/{slug}-card.png"


# --------- front-matter helpers for --post / --all backfill modes ---------

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_front_matter(text):
    m = FM_RE.match(text)
    if not m:
        return None, text
    fm = {}
    for line in m.group(1).splitlines():
        km = re.match(r'^(\w+):\s*(.*)$', line)
        if km:
            fm[km.group(1)] = km.group(2).strip().strip('"')
    return fm, text


def inject_image(post_path, image_path):
    text = post_path.read_text(encoding="utf-8")
    m = FM_RE.match(text)
    if not m:
        raise RuntimeError(f"{post_path} has no front matter to update")
    block = m.group(1)
    if re.search(r'^image:\s*', block, re.MULTILINE):
        block = re.sub(r'^image:\s*.*$', f"image: {image_path}", block, flags=re.MULTILINE)
    else:
        block = block.rstrip() + f"\nimage: {image_path}"
    new_text = text[:m.start(1)] + block + text[m.end(1):]
    post_path.write_text(new_text, encoding="utf-8")


def card_for_post(post_path, *, force=False):
    """Ensure a single post file has a card and an `image:` key.
    Returns the image path (existing or freshly generated), or None if skipped."""
    fm, text = parse_front_matter(post_path.read_text(encoding="utf-8"))
    if fm is None:
        print(f"  skip {post_path.name}: no front matter")
        return None
    if fm.get("image") and not force:
        return fm["image"]
    slug = post_path.stem
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug)
    title = fm.get("title") or slug.replace("-", " ").title()
    excerpt = fm.get("excerpt", "")
    image_path = generate_card(slug, title, excerpt)
    inject_image(post_path, image_path)
    print(f"  carded {post_path.name} -> {image_path}")
    return image_path


def main():
    parser = argparse.ArgumentParser(description="Generate a post social card.")
    parser.add_argument("--slug", help="Post slug (filename stem without date)")
    parser.add_argument("--title", help="Post title")
    parser.add_argument("--excerpt", default="", help="Post excerpt")
    parser.add_argument("--post", help="Path to a post file: read front matter, render, wire image")
    parser.add_argument("--all", action="store_true", help="Backfill every direct post missing a card")
    parser.add_argument("--force", action="store_true", help="Regenerate even if image already set")
    args = parser.parse_args()

    if args.all:
        posts = sorted(
            list((REPO_ROOT / "_posts").glob("*.html"))
            + list((REPO_ROOT / "_posts").glob("*.md"))
        )
        made = 0
        for p in posts:
            if card_for_post(p, force=args.force):
                made += 1
        print(f"Done. Ensured cards for {made}/{len(posts)} posts.")
        return

    if args.post:
        card_for_post(Path(args.post), force=args.force)
        return

    if not (args.slug and args.title):
        parser.error("provide --slug and --title (or use --post / --all)")
    image_path = generate_card(args.slug, args.title, args.excerpt)
    print(f"Created card: {image_path}")


if __name__ == "__main__":
    main()
