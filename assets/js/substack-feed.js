// Fetch and display Substack posts
async function fetchSubstackPosts() {
  const substackFeed = 'https://johndamask.substack.com/feed';
  const proxyUrl = 'https://api.rss2json.com/v1/api.json?rss_url=';

  try {
    const response = await fetch(proxyUrl + encodeURIComponent(substackFeed));
    const data = await response.json();

    if (data.status === 'ok') {
      return data.items.map(item => ({
        title: item.title,
        description: item.description,
        link: item.link,
        pubDate: new Date(item.pubDate),
        thumbnail: item.thumbnail || extractImageFromContent(item.content),
        source: 'substack'
      }));
    }
  } catch (error) {
    console.error('Error fetching Substack posts:', error);
    return [];
  }
  return [];
}

// Extract first image from HTML content
function extractImageFromContent(content) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(content, 'text/html');
  const img = doc.querySelector('img');
  return img ? img.src : null;
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

    const sourceLabel = post.source === 'substack'
      ? '<span class="post-source substack">Substack</span>'
      : '<span class="post-source blog">Blog</span>';

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
document.addEventListener('DOMContentLoaded', async function() {
  const substackPosts = await fetchSubstackPosts();
  const jekyllPosts = getJekyllPosts();
  const allPosts = [...substackPosts, ...jekyllPosts];

  renderCombinedPosts(allPosts);
});
