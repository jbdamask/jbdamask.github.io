---
name: Add Google Analytics Tag
description: >
  Add the site's Google Analytics gtag to HTML pages that are missing it
version: 1.0.0
tags: [analytics, gtag, google-analytics, html]
---

# Add Google Analytics Tag

This skill adds the Google Analytics tracking tag to HTML pages in this project.

## When to Use

Use this skill when you need to:
- Add Google Analytics tracking to a new HTML page
- Check if pages are missing the gtag and fix them
- Ensure all HTML files have consistent analytics tracking

## Site's Google Analytics ID

This project uses the following Google Analytics ID:

```
G-NYHKMP85KC
```

## The gtag Code Block

Add this code block immediately after the opening `<head>` tag and before any `<meta>` tags:

```html
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-NYHKMP85KC"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-NYHKMP85KC');
    </script>
```

## How to Add the gtag

1. Open the HTML file
2. Locate the `<head>` tag
3. Insert the gtag code block right after `<head>` and before the first `<meta charset="UTF-8">` tag
4. The structure should be:

```html
<head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-NYHKMP85KC"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-NYHKMP85KC');
    </script>
    <meta charset="UTF-8">
    <!-- rest of head content -->
</head>
```

## Finding Pages Missing the gtag

To find HTML files that don't have the gtag, search for HTML files and check which ones are missing `googletagmanager` or `gtag`:

1. List all HTML files in the project (especially in `tools/` directory)
2. Search for files containing `gtag` or `googletagmanager`
3. Compare to find any missing files
4. Add the gtag code block to missing files

## Verification

After adding the gtag, verify by:
1. Checking that the gtag code appears right after `<head>`
2. Confirming the Google Analytics ID is `G-NYHKMP85KC`
3. Testing the page loads without JavaScript errors
