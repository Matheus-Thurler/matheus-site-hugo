(function () {
  if (!window.__ANALYTICS_SELF_HOSTED__) return;
  var path = window.location.pathname;
  var postMatch = path.match(/\/posts\/([^/]+)\//);
  var payload = JSON.stringify({
    path: path,
    referrer: document.referrer || '',
    post_slug: postMatch ? postMatch[1] : '',
  });
  if (navigator.sendBeacon) {
    navigator.sendBeacon('/analytics/track/', new Blob([payload], { type: 'application/json' }));
  } else {
    fetch('/analytics/track/', { method: 'POST', body: payload, headers: { 'Content-Type': 'application/json' }, keepalive: true });
  }
})();
