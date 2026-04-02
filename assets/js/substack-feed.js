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
      source: el.dataset.source
    });
  });

  return posts;
}

// Get Now I Get It! DevLog posts from the page (fetched by GitHub Actions)
function getNowigetitPosts() {
  const posts = [];
  const postElements = document.querySelectorAll('.nowigetit-post-item');

  postElements.forEach(el => {
    posts.push({
      title: el.dataset.title,
      description: el.dataset.excerpt,
      link: el.dataset.url,
      pubDate: new Date(el.dataset.date),
      thumbnail: null,
      source: 'nowigetit'
    });
  });

  return posts;
}

// Render main posts in editorial format
function renderCombinedPosts(posts) {
  const container = document.getElementById('combined-posts');
  if (!container) return;

  // Filter out Twitter posts
  const mainPosts = posts.filter(p => p.source !== 'twitter');

  // Sort by date, newest first
  mainPosts.sort((a, b) => b.pubDate - a.pubDate);

  if (mainPosts.length === 0) {
    container.innerHTML = '<p class="ed-loading">No posts yet.</p>';
    return;
  }

  const html = mainPosts.map(post => {
    const dateStr = post.pubDate.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });

    let sourceClass = post.source || 'blog';
    let sourceLabel;
    if (sourceClass === 'nowigetit') {
      sourceLabel = 'Now I Get It!';
    } else {
      sourceLabel = sourceClass.charAt(0).toUpperCase() + sourceClass.slice(1);
    }

    // Clean description (strip HTML, limit length)
    const description = stripHtml(post.description);
    const truncated = description.length > 200 ? description.substring(0, 200) + '...' : description;

    return `
      <a href="${post.link}" class="ed-post-item" target="_blank" rel="noopener noreferrer">
        <div class="ed-post-item-content">
          <div class="ed-post-title">${post.title}</div>
          <p class="ed-post-excerpt">${truncated}</p>
        </div>
        <div class="ed-post-meta-right">
          <span class="ed-post-date">${dateStr}</span>
          <span class="ed-source-tag ${sourceClass}">${sourceLabel}</span>
        </div>
      </a>
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
  const nowigetitPosts = getNowigetitPosts();
  const allPosts = [...substackPosts, ...twitterPosts, ...jekyllPosts, ...externalPosts, ...nowigetitPosts];

  renderCombinedPosts(allPosts);
});
