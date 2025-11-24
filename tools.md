---
layout: single
title: Tools
permalink: /tools/
author_profile: true
---

A collection of standalone HTML tools and apps. Simply drop files into the `tools/` directory and they will automatically appear here!

<div class="tools-grid">
{% assign html_tools = site.static_files | where_exp: "file", "file.path contains 'tools/'" | where_exp: "file", "file.extname == '.html'" | sort: "basename" %}
{% assign doc_pages = site.pages | where_exp: "page", "page.path contains 'tools/'" | where_exp: "page", "page.path contains '.md'" %}

{% for tool in html_tools %}
  {% assign tool_name = tool.basename | replace: "-", " " | replace: "_", " " | capitalize %}

  <!-- Check if there's a matching .md documentation file -->
  {% assign has_docs = false %}
  {% assign doc_url = "" %}
  {% for doc in doc_pages %}
    {% assign doc_basename = doc.path | split: "/" | last | replace: ".md", "" %}
    {% if doc_basename == tool.basename %}
      {% assign has_docs = true %}
      {% assign doc_url = doc.url %}
      {% break %}
    {% endif %}
  {% endfor %}

  <div class="tool-card">
    <h3>
      {% if has_docs %}
        <a href="{{ doc_url | relative_url }}">{{ tool_name }}</a>
      {% else %}
        <a href="{{ tool.path | relative_url }}">{{ tool_name }}</a>
      {% endif %}
    </h3>
    <p class="tool-link">
      {% if has_docs %}
        <a href="{{ doc_url | relative_url }}" class="btn btn--info">Learn More</a>
        <a href="{{ tool.path | relative_url }}" class="btn btn--primary">Launch →</a>
      {% else %}
        <a href="{{ tool.path | relative_url }}" class="btn btn--primary">Launch Tool →</a>
      {% endif %}
    </p>
  </div>
{% endfor %}

{% if html_tools.size == 0 %}
  <p class="no-tools">No tools available yet. Add HTML files to the <code>tools/</code> directory to see them here!</p>
{% endif %}
</div>

---

### How to Add a New Tool

#### Option 1: Simple Tool (HTML only)
1. Create a standalone HTML file (e.g., `my-tool.html`)
2. Copy it to the `tools/` directory
3. Commit and push - done!

#### Option 2: Tool with Documentation (HTML + Markdown)
1. Create your tool HTML file (e.g., `pretty-markdown.html`)
2. Create a matching markdown file (e.g., `pretty-markdown.md`) with:
   ```yaml
   ---
   title: Pretty Markdown
   tool_url: /tools/pretty-markdown.html
   excerpt: A beautiful markdown renderer with syntax highlighting
   permalink: /tools/pretty-markdown/
   ---

   ## About
   Description of your tool here...

   ## Features
   - Feature 1
   - Feature 2
   ```
3. Copy both files to `tools/`
4. Commit and push!

The tools page will automatically:
- Show a "Learn More" button (links to the .md documentation)
- Show a "Launch →" button (launches the .html tool)
- If no .md file exists, just shows "Launch Tool →"

<style>
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.tool-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  background: #f9f9f9;
  transition: transform 0.2s, box-shadow 0.2s;
}

.tool-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.tool-card h3 {
  margin-top: 0;
  font-size: 1.2rem;
}

.tool-card h3 a {
  text-decoration: none;
  color: #494e52;
}

.tool-card h3 a:hover {
  color: #0066cc;
}

.btn--primary {
  display: inline-block;
  padding: 0.5rem 1rem;
  background-color: #0066cc;
  color: white !important;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.btn--primary:hover {
  background-color: #0052a3;
}

.btn--info {
  display: inline-block;
  padding: 0.5rem 1rem;
  background-color: #17a2b8;
  color: white !important;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.2s;
  margin-right: 0.5rem;
}

.btn--info:hover {
  background-color: #138496;
}

.tool-link {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
</style>
