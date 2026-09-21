(() => {
  const el = document.getElementById("consent");
  const btn = document.getElementById("consent-accept");
  const key = "cookie-consent-accepted";
  const cfg = window.__siteConsent || {};

  window.dataLayer = window.dataLayer || [];
  window.gtag =
    window.gtag ||
    function gtag() {
      window.dataLayer.push(arguments);
    };
  window.gtag("consent", "default", {
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied",
    analytics_storage: "denied",
    wait_for_update: 500,
  });

  const loadScript = (src, attrs = {}) => {
    if ([...document.scripts].some((s) => s.src === src || s.getAttribute("src") === src)) {
      return;
    }
    const script = document.createElement("script");
    script.src = src;
    script.async = true;
    Object.entries(attrs).forEach(([name, value]) => {
      script.setAttribute(name, value);
    });
    document.head.appendChild(script);
  };

  const enableTracking = () => {
    window.gtag("consent", "update", {
      ad_storage: "granted",
      ad_user_data: "granted",
      ad_personalization: "granted",
      analytics_storage: "granted",
    });
    if (cfg.gaId) {
      loadScript(`https://www.googletagmanager.com/gtag/js?id=${cfg.gaId}`);
      window.gtag("js", new Date());
      window.gtag("config", cfg.gaId, { anonymize_ip: true });
    }
    if (cfg.adsense) {
      loadScript(
        `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${cfg.adsense}`,
        { crossorigin: "anonymous", "data-overlays": "bottom" }
      );
    }
  };

  if (localStorage.getItem(key)) {
    enableTracking();
    if (el) el.hidden = true;
    return;
  }

  if (!el || !btn) return;
  el.hidden = false;
  document.body.classList.add("has-consent");
  btn.addEventListener("click", () => {
    localStorage.setItem(key, "true");
    el.hidden = true;
    document.body.classList.remove("has-consent");
    enableTracking();
  });
})();
