---
layout: single
title: Posts
permalink: /posts/
author_profile: true
---

<div id="combined-posts" class="posts-grid">
  <p class="loading">Loading posts...</p>
</div>

<!-- Hidden Jekyll post data for JavaScript -->
<div style="display: none;">
{% for post in site.posts %}
  <div class="jekyll-post-item"
       data-title="{{ post.title | xml_escape }}"
       data-excerpt="{{ post.excerpt | strip_html | xml_escape }}"
       data-url="{{ post.url | relative_url }}"
       data-date="{{ post.date | date_to_xmlschema }}"
       data-image="{{ post.image | default: '' }}">
  </div>
{% endfor %}

<!-- External posts (LinkedIn) -->
{% for post in site.data.external-posts %}
  <div class="external-post-item"
       data-title="{{ post.title | xml_escape }}"
       data-excerpt="{{ post.excerpt | xml_escape }}"
       data-url="{{ post.url }}"
       data-date="{{ post.date | date_to_xmlschema }}"
       data-image="{{ post.image | default: '' }}"
       data-source="{{ post.source }}">
  </div>
{% endfor %}

<!-- Twitter posts (from GitHub Actions) -->
{% if site.data.twitter-posts %}
{% for post in site.data.twitter-posts %}
  <div class="twitter-post-item"
       data-title="{{ post.title | xml_escape }}"
       data-excerpt="{{ post.excerpt | xml_escape }}"
       data-url="{{ post.url }}"
       data-date="{{ post.date | date_to_xmlschema }}"
       data-image="{{ post.image | default: '' }}">
  </div>
{% endfor %}
{% endif %}
</div>

<style>
.posts-grid {
  display: grid;
  gap: 2rem;
  margin-top: 2rem;
}

.post-card {
  display: flex;
  gap: 1.5rem;
  padding: 1.5rem;
  background: #f9f9f9;
  border-radius: 8px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.post-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.post-thumbnail {
  width: 200px;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
  flex-shrink: 0;
}

.post-content {
  flex: 1;
}

.post-meta {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.post-source {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
}

.post-source.substack {
  background: #FF6719;
  color: white;
}

.post-source.blog {
  background: #0066cc;
  color: white;
}

.post-source.twitter {
  background: #1DA1F2;
  color: white;
}

.post-date {
  color: #666;
}

.post-card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
}

.post-card h3 a {
  color: #333;
  text-decoration: none;
}

.post-card h3 a:hover {
  color: #0066cc;
}

.post-excerpt {
  color: #666;
  line-height: 1.6;
  margin: 0;
}

.loading {
  text-align: center;
  color: #666;
  padding: 2rem;
}

/* Responsive */
@media (max-width: 768px) {
  .post-card {
    flex-direction: column;
  }

  .post-thumbnail {
    width: 100%;
    height: 200px;
  }
}
</style>

<script src="{{ '/assets/js/substack-feed.js' | relative_url }}"></script>
