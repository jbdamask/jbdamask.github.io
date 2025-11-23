---
layout: single
title: Tools
permalink: /tools/
author_profile: true
---

A collection of standalone HTML tools and apps. Simply drop an HTML file into the `tools/` directory and it will automatically appear here!

<div class="tools-grid">
{% assign tool_files = site.static_files | where_exp: "file", "file.path contains 'tools/'" | where_exp: "file", "file.extname == '.html'" | sort: "basename" %}

{% for tool in tool_files %}
  {% assign tool_name = tool.basename | replace: "-", " " | replace: "_", " " | capitalize %}
  <div class="tool-card">
    <h3><a href="{{ tool.path | relative_url }}">{{ tool_name }}</a></h3>
    <p class="tool-link"><a href="{{ tool.path | relative_url }}" class="btn btn--primary">Launch Tool →</a></p>
  </div>
{% endfor %}

{% if tool_files.size == 0 %}
  <p class="no-tools">No tools available yet. Add HTML files to the <code>tools/</code> directory to see them here!</p>
{% endif %}
</div>

---

### How to Add a New Tool

1. Create a standalone HTML file (e.g., `my-tool.html`)
2. Copy it to the `tools/` directory
3. Commit and push - the tool will automatically appear on this page!

**Optional:** Add a description meta tag in your HTML:
```html
<meta name="tool-description" content="Description of your tool">
```

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
</style>
