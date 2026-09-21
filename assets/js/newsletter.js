(() => {
  document.querySelectorAll("[data-newsletter]").forEach((root) => {
    const form = root.querySelector("form");
    const msg = root.querySelector(".newsletter-msg");
    if (!form || !msg) return;
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      msg.hidden = false;
      msg.classList.remove("is-ok", "is-err");
      const data = { email: form.email.value, name: form.name.value };
      try {
        const res = await fetch(form.action, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });
        const json = await res.json().catch(() => ({}));
        if (res.ok) {
          msg.classList.add("is-ok");
          msg.textContent = msg.dataset.ok || "ok";
          form.reset();
        } else {
          msg.classList.add("is-err");
          msg.textContent = json.error || msg.dataset.err || "error";
        }
      } catch {
        msg.classList.add("is-err");
        msg.textContent = msg.dataset.err || "error";
      }
    });
  });
})();
