function getCookie(name) {
  const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
  return match ? decodeURIComponent(match[2]) : '';
}

document.addEventListener('DOMContentLoaded', () => {
  const section = document.getElementById('post-feedback');
  if (!section) return;
  const url = section.dataset.feedbackUrl;
  const stats = document.getElementById('feedback-stats');
  section.querySelectorAll('[data-helpful]').forEach((button) => {
    button.addEventListener('click', async () => {
      const body = new URLSearchParams();
      body.set('helpful', button.dataset.helpful);
      const resp = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body,
      });
      if (!resp.ok) return;
      const data = await resp.json();
      if (stats) stats.textContent = `${data.helpful}/${data.total} found helpful`;
      section.querySelectorAll('button').forEach((btn) => { btn.disabled = true; });
    });
  });
});
