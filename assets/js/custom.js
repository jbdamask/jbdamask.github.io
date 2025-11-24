// Make all social media links open in new tab
document.addEventListener('DOMContentLoaded', function() {
  // Target all author links (social media)
  const authorLinks = document.querySelectorAll('.author__urls a');

  authorLinks.forEach(function(link) {
    // Only add target="_blank" to external links (not email)
    if (!link.href.startsWith('mailto:')) {
      link.setAttribute('target', '_blank');
      link.setAttribute('rel', 'noopener noreferrer');
    }
  });
});
