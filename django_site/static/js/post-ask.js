function getCookie(name) {
  const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
  return match ? decodeURIComponent(match[2]) : '';
}

document.addEventListener('DOMContentLoaded', () => {
  const section = document.getElementById('post-ask');
  if (!section) return;
  const url = section.dataset.askUrl;
  const input = document.getElementById('post-ask-input');
  const button = document.getElementById('post-ask-btn');
  const answer = document.getElementById('post-ask-answer');
  button.addEventListener('click', async () => {
    const question = (input.value || '').trim();
    if (!question) return;
    button.disabled = true;
    const body = new URLSearchParams();
    body.set('question', question);
    const resp = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body,
    });
    button.disabled = false;
    if (!resp.ok) return;
    const data = await resp.json();
    answer.textContent = data.answer || '';
    answer.classList.remove('hidden');
  });
});
