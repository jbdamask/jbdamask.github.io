#!/usr/bin/env python3
"""
Convert MHTML files to blog posts with Jekyll front matter
Usage: python scripts/convert_mhtml.py input.mhtml [--title "Post Title"]
"""

import sys
import re
import quopri
from pathlib import Path
from datetime import datetime
import argparse
from urllib.parse import urlparse

def convert_mhtml_to_html(mhtml_path, output_path):
    """Convert MHTML file to standalone HTML"""

    # Read the MHTML file
    with open(mhtml_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Extract the main snapshot URL to identify the primary content
    snapshot_match = re.search(r'Snapshot-Content-Location:\s*(.+)', content)
    snapshot_domain = None
    if snapshot_match:
        snapshot_url = snapshot_match.group(1).strip()
        snapshot_domain = urlparse(snapshot_url).netloc

    # Find the boundary marker
    boundary_match = re.search(r'boundary="([^"]+)"', content)
    if not boundary_match:
        boundary_match = re.search(r'boundary=([^\s;]+)', content)

    if not boundary_match:
        print("Error: Could not find boundary marker in MHTML file")
        return False

    boundary = boundary_match.group(1)

    # Split by boundary
    parts = content.split(f'--{boundary}')

    html_parts = []  # Store all HTML parts with their metadata

    # Extract HTML parts only (skip CSS - external links in HTML are sufficient)
    for part in parts:
        # Check content type
        if 'Content-Type: text/html' in part:
            # Extract Content-Location if present
            location_match = re.search(r'Content-Location:\s*(.+)', part)
            part_url = location_match.group(1).strip() if location_match else None
            part_domain = urlparse(part_url).netloc if part_url else None

            # Extract HTML content (skip all headers until blank line)
            # MHTML format has headers, then blank line, then content
            match = re.search(r'\n\n(.+)', part, re.DOTALL)
            if match:
                html_encoded = match.group(1).strip()
                # Decode quoted-printable
                decoded_html = quopri.decodestring(html_encoded.encode()).decode('utf-8', errors='ignore')
                html_parts.append({
                    'content': decoded_html,
                    'domain': part_domain,
                    'url': part_url
                })

    # Choose the best HTML part
    html_content = None
    if html_parts:
        # Prefer HTML part from the same domain as snapshot
        if snapshot_domain:
            for part in html_parts:
                if part['domain'] == snapshot_domain:
                    html_content = part['content']
                    break

        # Fall back to first HTML part if no domain match
        if html_content is None:
            html_content = html_parts[0]['content']

    if not html_content:
        print("Error: No HTML content found in MHTML file")
        return False

    # Remove internal CSS references (cid: links) - these won't work in the output
    html_content = re.sub(r'<link[^>]*href="cid:[^"]*"[^>]*>', '', html_content)

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✓ Converted {mhtml_path} → {output_path}")
    print(f"  File size: {Path(output_path).stat().st_size / 1024:.1f} KB")
    return True

def extract_text_preview(html, max_length=200):
    """Extract plain text preview from HTML"""
    # Remove script and style tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Truncate
    if len(text) > max_length:
        text = text[:max_length] + '...'
    return text

def create_blog_post(title, html_content, date=None):
    """Create Jekyll blog post with front matter"""
    if date is None:
        date = datetime.now()

    date_str = date.strftime('%Y-%m-%d')

    # Extract excerpt from HTML
    excerpt = extract_text_preview(html_content)

    # Create front matter
    front_matter = f"""---
layout: app
title: "{title}"
date: {date_str}
excerpt: "{excerpt}"
---

"""

    return front_matter + html_content

def main():
    parser = argparse.ArgumentParser(
        description='Convert MHTML to Jekyll blog post',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage - auto-generates title and filename
  python scripts/convert_mhtml.py my-app-output.mhtml

  # Specify custom title
  python scripts/convert_mhtml.py my-app-output.mhtml --title "Beatbox Analysis Results"

  # Specify custom output filename
  python scripts/convert_mhtml.py my-app-output.mhtml --output _posts/2025-11-24-custom-name.html
        """
    )

    parser.add_argument('input', help='Input MHTML file')
    parser.add_argument('--title', '-t', help='Post title (default: derived from filename)')
    parser.add_argument('--output', '-o', help='Output file path (default: _posts/YYYY-MM-DD-title.html)')
    parser.add_argument('--date', '-d', help='Post date (default: today, format: YYYY-MM-DD)')

    args = parser.parse_args()

    input_file = args.input

    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)

    # Parse date
    if args.date:
        try:
            post_date = datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
    else:
        post_date = datetime.now()

    # Generate title if not provided
    if args.title:
        title = args.title
    else:
        # Use filename without extension as title
        title = Path(input_file).stem.replace('-', ' ').replace('_', ' ').title()

    # Generate output filename if not provided
    if args.output:
        output_file = args.output
    else:
        # Create filename from title and date
        date_str = post_date.strftime('%Y-%m-%d')
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[\s_]+', '-', slug)
        output_file = f"_posts/{date_str}-{slug}.html"

    # Create output directory if needed
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # Convert MHTML to HTML
    temp_file = output_file + '.tmp'
    success = convert_mhtml_to_html(input_file, temp_file)

    if not success:
        sys.exit(1)

    # Read converted HTML
    with open(temp_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Create blog post with front matter
    blog_post = create_blog_post(title, html_content, post_date)

    # Write final file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(blog_post)

    # Remove temp file
    Path(temp_file).unlink()

    print(f"\n✓ Created blog post: {output_file}")
    print(f"  Title: {title}")
    print(f"  Date: {post_date.strftime('%Y-%m-%d')}")
    print(f"\nNext steps:")
    print(f"  git add {output_file}")
    print(f"  git commit -m 'Add post: {title}'")
    print(f"  git push")

if __name__ == '__main__':
    main()
