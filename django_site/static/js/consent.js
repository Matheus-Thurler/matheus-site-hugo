/**
 * Cookie consent + lazy-load third-party scripts (GA, AdSense, Giscus).
 * Scripts load only after explicit user acceptance (LGPD/GDPR).
 */
(function () {
  "use strict";

  const CONSENT_KEY = "cookie-consent";
  const BANNER_ID = "cookie-consent";

  function loadScript(src, attributes) {
    return new Promise(function (resolve, reject) {
      const script = document.createElement("script");
      script.src = src;
      script.async = true;
      if (attributes) {
        Object.entries(attributes).forEach(function ([key, value]) {
          if (value !== null && value !== undefined) {
            script.setAttribute(key, value);
          }
        });
      }
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  function loadGoogleAnalytics() {
    if (!window.__ANALYTICS_ENABLED__ || !window.__GA_ID__) return;

    loadScript("https://www.googletagmanager.com/gtag/js?id=" + window.__GA_ID__)
      .then(function () {
        window.dataLayer = window.dataLayer || [];
        function gtag() {
          window.dataLayer.push(arguments);
        }
        window.gtag = gtag;
        gtag("js", new Date());
        gtag("config", window.__GA_ID__, { anonymize_ip: true });
      })
      .catch(function () {});
  }

  function loadAdSense() {
    if (!window.__ADSENSE_ID__) return;

    var link = document.createElement("link");
    link.rel = "preconnect";
    link.href = "https://pagead2.googlesyndication.com";
    link.crossOrigin = "anonymous";
    document.head.appendChild(link);

    loadScript(
      "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" +
        window.__ADSENSE_ID__,
      { crossorigin: "anonymous" }
    )
      .then(function () {
        initAdSlots();
      })
      .catch(function () {});
  }

  function initAdSlots() {
    document.querySelectorAll(".adsense-slot").forEach(function (slot) {
      slot.classList.remove("hidden");
      var ins = slot.querySelector("ins.adsbygoogle");
      if (!ins || ins.dataset.initialized === "true") return;
      try {
        (window.adsbygoogle = window.adsbygoogle || []).push({});
        ins.dataset.initialized = "true";
      } catch (err) {
        /* adsbygoogle not ready */
      }
    });
  }

  function loadGiscus() {
    var root = document.getElementById("giscus-root");
    if (!root || root.dataset.loaded === "true") return;

    var script = document.createElement("script");
    script.src = "https://giscus.app/client.js";
    script.async = true;
    script.crossOrigin = "anonymous";
    script.setAttribute("data-repo", root.dataset.repo || "");
    script.setAttribute("data-repo-id", root.dataset.repoId || "");
    script.setAttribute("data-category", root.dataset.category || "");
    script.setAttribute("data-category-id", root.dataset.categoryId || "");
    script.setAttribute("data-mapping", root.dataset.mapping || "pathname");
    script.setAttribute("data-strict", "0");
    script.setAttribute(
      "data-reactions-enabled",
      root.dataset.reactionsEnabled || "1"
    );
    script.setAttribute(
      "data-emit-metadata",
      root.dataset.emitMetadata || "0"
    );
    script.setAttribute(
      "data-input-position",
      root.dataset.inputPosition || "bottom"
    );
    script.setAttribute(
      "data-theme",
      root.dataset.theme || "preferred_color_scheme"
    );
    script.setAttribute("data-lang", root.dataset.lang || "en");
    root.appendChild(script);
    root.dataset.loaded = "true";
  }

  function loadThirdParties() {
    loadGoogleAnalytics();
    loadAdSense();
    loadGiscus();
  }

  function hideBanner(banner) {
    banner.classList.remove("cookie-consent--visible");
    window.setTimeout(function () {
      banner.classList.add("hidden");
    }, 300);
  }

  function setConsent(value) {
    localStorage.setItem(CONSENT_KEY, value);
    localStorage.setItem("cookie-consent-date", new Date().toISOString());

    if (value === "accepted") {
      loadThirdParties();
    }

    var banner = document.getElementById(BANNER_ID);
    if (banner) hideBanner(banner);
  }

  function initBanner() {
    var banner = document.getElementById(BANNER_ID);
    if (!banner) return;

    if (localStorage.getItem(CONSENT_KEY)) return;

    window.requestAnimationFrame(function () {
      banner.classList.remove("hidden", "pointer-events-none");
      banner.classList.add("cookie-consent--visible");
    });

    document.getElementById("cookie-accept")?.addEventListener("click", function () {
      setConsent("accepted");
    });
    document.getElementById("cookie-reject")?.addEventListener("click", function () {
      setConsent("rejected");
    });
    document.getElementById("cookie-close")?.addEventListener("click", function () {
      setConsent("dismissed");
    });
  }

  function init() {
    if (localStorage.getItem(CONSENT_KEY) === "accepted") {
      loadThirdParties();
    }
    initBanner();
  }

  window.MTConsent = {
    accept: loadThirdParties,
    setConsent: setConsent,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
