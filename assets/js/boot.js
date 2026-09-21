(() => {
  const overlay = document.getElementById("boot");
  if (!overlay) return;

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const seen = sessionStorage.getItem("vf-boot-seen") === "1";
  if (reduce || seen) {
    overlay.remove();
    return;
  }

  const finish = () => {
    overlay.classList.add("is-done");
    sessionStorage.setItem("vf-boot-seen", "1");
    window.setTimeout(() => overlay.remove(), 420);
  };

  overlay.removeAttribute("hidden");
  overlay.querySelector("[data-boot-skip]")?.addEventListener("click", finish);
  window.setTimeout(finish, 3000);
})();
