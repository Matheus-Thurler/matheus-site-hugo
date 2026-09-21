(() => {
  const textOf = (block) => {
    const lines = block.querySelectorAll(".chroma .cl");
    if (lines.length) {
      return [...lines].map((line) => line.textContent).join("\n");
    }
    return block.querySelector("code")?.innerText ?? "";
  };

  const copyText = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.top = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      const ok = document.execCommand("copy");
      ta.remove();
      return ok;
    }
  };

  document.querySelectorAll("[data-copy]").forEach((btn) => {
    const copyLabel = btn.dataset.labelCopy || "Copy";
    const copiedLabel = btn.dataset.labelCopied || "Copied";
    btn.addEventListener("click", async () => {
      const block = btn.closest(".code-block");
      if (!block) return;
      const ok = await copyText(textOf(block));
      if (!ok) return;
      btn.textContent = copiedLabel;
      window.setTimeout(() => {
        btn.textContent = copyLabel;
      }, 1600);
    });
  });
})();
