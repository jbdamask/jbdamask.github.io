---
layout: single
title: Tools
permalink: /tools/
author_profile: true
---

This page is where I store little tools that I've built. Currently, they're just single page web apps. I may eventually host more sophisticated ones here but that's really TBD. 

See my [GitHub](https://github.com/jbdamask) for source code of these and more.

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
