/**
 * YouTube click-to-play facades — no third-party cookies until user clicks.
 */
(function () {
  "use strict";

  function activateFacade(facade) {
    if (facade.dataset.loaded === "true") return;

    var videoId = facade.dataset.videoId;
    var title = facade.dataset.title || "YouTube video";
    if (!videoId) return;

    var iframe = document.createElement("iframe");
    iframe.className = "youtube-embed h-full w-full rounded-md border-0";
    iframe.src =
      "https://www.youtube-nocookie.com/embed/" +
      encodeURIComponent(videoId) +
      "?autoplay=1";
    iframe.title = title;
    iframe.loading = "lazy";
    iframe.allow =
      "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
    iframe.referrerPolicy = "strict-origin-when-cross-origin";
    iframe.allowFullscreen = true;

    facade.replaceChildren(iframe);
    facade.dataset.loaded = "true";
  }

  function init() {
    document.querySelectorAll(".youtube-facade").forEach(function (facade) {
      facade.addEventListener("click", function () {
        activateFacade(facade);
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
