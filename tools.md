---
layout: editorial-page
title: Tools
permalink: /tools/
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

  <!-- External tools (hosted outside this site) -->
  <div class="tool-card">
    <h3>
      <a href="https://github.com/jbdamask/john-claude-skills">John Claude Skills</a>
    </h3>
    <p>A collection of Claude Code skills I use day to day.</p>
    <p class="tool-link">
      <a href="https://github.com/jbdamask/john-claude-skills" class="btn btn--primary">View on GitHub →</a>
    </p>
  </div>

{% if html_tools.size == 0 %}
  <p class="no-tools">No tools available yet. Add HTML files to the <code>tools/</code> directory to see them here!</p>
{% endif %}
</div>

---

