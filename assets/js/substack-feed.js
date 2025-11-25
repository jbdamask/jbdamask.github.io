// Get Substack posts from the page (fetched by GitHub Actions)
function getSubstackPosts() {
  const posts = [];
  const postElements = document.querySelectorAll('.substack-post-item');

  postElements.forEach(el => {
    posts.push({
      title: el.dataset.title,
      description: el.dataset.excerpt,
      link: el.dataset.url,
      pubDate: new Date(el.dataset.date),
      thumbnail: el.dataset.image || null,
      source: 'substack'
    });
  });

  return posts;
}

// Get Twitter posts from the page (fetched by GitHub Actions)
function getTwitterPosts() {
  const posts = [];
  const postElements = document.querySelectorAll('.twitter-post-item');

  postElements.forEach(el => {
    posts.push({
      title: el.dataset.title,
      description: el.dataset.excerpt,
      link: el.dataset.url,
      pubDate: new Date(el.dataset.date),
      thumbnail: el.dataset.image || null,
      source: 'twitter'
    });
  });

  return posts;
}

// Get Jekyll posts from the page
function getJekyllPosts() {
  const posts = [];
  const postElements = document.querySelectorAll('.jekyll-post-item');

  postElements.forEach(el => {
    posts.push({
      title: el.dataset.title,
      description: el.dataset.excerpt,
      link: el.dataset.url,
      pubDate: new Date(el.dataset.date),
      thumbnail: el.dataset.image || null,
      source: 'blog'
    });
  });

  return posts;
}

// Get external posts (LinkedIn, Twitter, etc.) from the page
function getExternalPosts() {
  const posts = [];
  const postElements = document.querySelectorAll('.external-post-item');

  postElements.forEach(el => {
    posts.push({
      title: el.dataset.title,
      description: el.dataset.excerpt,
      link: el.dataset.url,
      pubDate: new Date(el.dataset.date),
      thumbnail: el.dataset.image || null,
      source: el.dataset.source // 'linkedin' or 'twitter'
    });
  });

  return posts;
}

// Render combined posts
function renderCombinedPosts(posts) {
  const container = document.getElementById('combined-posts');
  if (!container) return;

  // Sort by date, newest first
  posts.sort((a, b) => b.pubDate - a.pubDate);

  if (posts.length === 0) {
    container.innerHTML = '<p>No posts yet.</p>';
    return;
  }

  const html = posts.map(post => {
    const dateStr = post.pubDate.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });

    let sourceLabel;
    if (post.source === 'substack') {
      sourceLabel = '<span class="post-source substack">Substack</span>';
    } else if (post.source === 'twitter') {
      sourceLabel = '<span class="post-source twitter">Twitter</span>';
    } else if (post.source === 'linkedin') {
      sourceLabel = '<span class="post-source linkedin">LinkedIn</span>';
    } else {
      sourceLabel = '<span class="post-source blog">Blog</span>';
    }

    const thumbnail = post.thumbnail
      ? `<img src="${post.thumbnail}" alt="${post.title}" class="post-thumbnail">`
      : '';

    // Clean description (strip HTML, limit length)
    const description = stripHtml(post.description).substring(0, 200) + '...';

    return `
      <article class="post-card">
        ${thumbnail}
        <div class="post-content">
          <div class="post-meta">
            ${sourceLabel}
            <span class="post-date">${dateStr}</span>
          </div>
          <h3><a href="${post.link}" target="_blank" rel="noopener noreferrer">${post.title}</a></h3>
          <p class="post-excerpt">${description}</p>
        </div>
      </article>
    `;
  }).join('');

  container.innerHTML = html;
}

// Strip HTML tags
function stripHtml(html) {
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || '';
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
  const substackPosts = getSubstackPosts();
  const twitterPosts = getTwitterPosts();
  const jekyllPosts = getJekyllPosts();
  const externalPosts = getExternalPosts();
  const allPosts = [...substackPosts, ...twitterPosts, ...jekyllPosts, ...externalPosts];

  renderCombinedPosts(allPosts);
});
