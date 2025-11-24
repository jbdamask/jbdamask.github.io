# Adding HTML and MHTML Pages

## Adding HTML Pages

### Method 1: HTML with Jekyll Layout (Recommended)

Create an `.html` file anywhere in your site:

```html
---
layout: single
title: "My Page"
permalink: /my-page/
author_profile: true
---

<h2>Your Content</h2>
<p>Any HTML here...</p>
```

**Access at**: `https://yourdomain.com/my-page/`

### Method 2: Standalone HTML (No Layout)

Create an `.html` file without front matter:

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Standalone Page</title>
</head>
<body>
    <h1>Standalone HTML</h1>
</body>
</html>
```

**Access at**: `https://yourdomain.com/filename.html`

### Method 3: HTML in Subdirectories

Organize HTML files in folders:

```
/projects/
  /project1/
    index.html      → /projects/project1/
  /project2/
    index.html      → /projects/project2/
```

## Adding MHTML Pages

MHTML (MIME HTML) files are email/archive formats. Browsers don't render them well directly.

### Option A: Convert MHTML to HTML

**Using Python:**
```bash
pip install mhtml2html
mhtml2html input.mhtml output.html
```

**Using Online Tools:**
- https://www.zamzar.com/convert/mhtml-to-html/
- https://convertio.co/mhtml-html/

**Manual Extraction:**
1. Open MHTML in a text editor
2. Find the HTML content section
3. Copy the HTML between `Content-Type: text/html` boundaries
4. Save as `.html`

### Option B: Serve MHTML Directly (Not Recommended)

```html
---
layout: single
title: "View MHTML"
---

<p>Download the file:</p>
<a href="/assets/files/document.mhtml" download>Download MHTML</a>
```

Users will need to download and open locally.

## Examples

### Example 1: Project Page

File: `projects.html`
```html
---
layout: single
title: "My Projects"
permalink: /projects/
---

<div class="projects-grid">
  <div class="project">
    <h3>Project 1</h3>
    <p>Description...</p>
  </div>
</div>
```

### Example 2: Interactive Tool

File: `tools/calculator.html`
```html
---
layout: single
title: "Calculator"
permalink: /tools/calculator/
---

<input type="number" id="num1">
<input type="number" id="num2">
<button onclick="calculate()">Calculate</button>
<div id="result"></div>

<script>
function calculate() {
  const a = document.getElementById('num1').value;
  const b = document.getElementById('num2').value;
  document.getElementById('result').textContent = +a + +b;
}
</script>
```

## Directory Structure

```
/
├── page1.html              → /page1.html
├── example-page.html       → /example-page/
├── projects/
│   └── index.html         → /projects/
├── tools/
│   ├── tool1.html         → /tools/tool1.html
│   └── tool2.html         → /tools/tool2.html
└── assets/
    └── files/
        └── document.mhtml → /assets/files/document.mhtml
```

## Tips

1. **Use permalinks** in front matter for clean URLs
2. **Organize by topic** in subdirectories
3. **Convert MHTML to HTML** for better compatibility
4. **Test locally** with `bundle exec jekyll serve`
5. **Link from navigation** by editing `_data/navigation.yml`

## Converting MHTML Script

Here's a quick Python script to convert MHTML to HTML:

```python
import re

def mhtml_to_html(mhtml_file, output_file):
    with open(mhtml_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find HTML content between boundaries
    html_match = re.search(r'Content-Type: text/html.*?\n\n(.*?)(?=\n--)', content, re.DOTALL)

    if html_match:
        html_content = html_match.group(1)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Converted {mhtml_file} to {output_file}")
    else:
        print("Could not find HTML content in MHTML file")

# Usage
mhtml_to_html('input.mhtml', 'output.html')
```
