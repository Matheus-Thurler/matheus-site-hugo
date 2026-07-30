/**
 * Cookie consent + lazy third-party scripts (GA via Partytown, Giscus).
 * AdSense loads from adsense_head.html (same as Hugo — not gated by consent).
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

  function ensurePartytown() {
    if (!window.__PARTYTOWN_LIB__) {
      return Promise.resolve(false);
    }
    if (window.__partytownReady) {
      return Promise.resolve(true);
    }
    window.partytown = {
      forward: ["dataLayer.push", "gtag"],
      lib: window.__PARTYTOWN_LIB__,
    };
    return loadScript(window.__PARTYTOWN_LIB__ + "partytown.js").then(function () {
      window.__partytownReady = true;
      return true;
    });
  }

  function loadGoogleAnalytics() {
    if (
      !window.__ANALYTICS_ENABLED__ ||
      !window.__GA_ID__ ||
      window.__ANALYTICS_SELF_HOSTED__
    ) {
      return;
    }

    ensurePartytown()
      .then(function (ready) {
        var scriptType = ready ? "text/partytown" : "text/javascript";

        var configScript = document.createElement("script");
        configScript.type = scriptType;
        configScript.textContent =
          'window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}' +
          'gtag("js",new Date());gtag("config","' +
          window.__GA_ID__ +
          '",{anonymize_ip:true});';
        document.head.appendChild(configScript);

        var loader = document.createElement("script");
        loader.type = scriptType;
        loader.src =
          "https://www.googletagmanager.com/gtag/js?id=" + window.__GA_ID__;
        document.head.appendChild(loader);
      })
      .catch(function () {
        /* Partytown unavailable — skip GA rather than block main thread */
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

  function initGiscusLazy() {
    var root = document.getElementById("giscus-root");
    if (!root) return;

    if (!("IntersectionObserver" in window)) {
      loadGiscus();
      return;
    }

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            loadGiscus();
            observer.disconnect();
          }
        });
      },
      { rootMargin: "200px 0px" }
    );
    observer.observe(root);
  }

  function loadThirdParties() {
    scheduleIdle(loadGoogleAnalytics);
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
    initGiscusLazy();
    if (localStorage.getItem(CONSENT_KEY) === "accepted") {
      loadThirdParties();
    }
    scheduleIdle(initBanner);
  }

  function scheduleIdle(fn) {
    if ("requestIdleCallback" in window) {
      requestIdleCallback(fn, { timeout: 2500 });
    } else {
      setTimeout(fn, 1);
    }
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
