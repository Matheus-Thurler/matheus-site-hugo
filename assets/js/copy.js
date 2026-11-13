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
      return false;
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
