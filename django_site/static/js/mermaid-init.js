function getMermaidTheme() {
  return document.documentElement.classList.contains('dark') ? 'dark' : 'default';
}

function storeOriginalMermaidCode() {
  document.querySelectorAll('.mermaid').forEach((element) => {
    if (!element.getAttribute('data-original-code')) {
      element.setAttribute('data-original-code', element.textContent.trim());
    }
  });
}

async function renderMermaidDiagrams() {
  const { default: mermaid } = await import(
    'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs'
  );

  mermaid.initialize({
    startOnLoad: false,
    theme: getMermaidTheme(),
    securityLevel: 'loose',
  });

  storeOriginalMermaidCode();
  await mermaid.run();
  return mermaid;
}

let mermaidModulePromise = null;

function initMermaid() {
  if (!document.querySelector('.mermaid')) {
    return;
  }

  if (!mermaidModulePromise) {
    mermaidModulePromise = renderMermaidDiagrams();
  }

  window.addEventListener('themeChanged', async () => {
    if (!mermaidModulePromise) {
      return;
    }

    try {
      const mermaid = await mermaidModulePromise;
      document.querySelectorAll('.mermaid').forEach((element) => {
        const originalCode = element.getAttribute('data-original-code');
        if (originalCode) {
          element.removeAttribute('data-processed');
          element.textContent = originalCode;
        }
      });

      mermaid.initialize({
        startOnLoad: false,
        theme: getMermaidTheme(),
        securityLevel: 'loose',
      });
      await mermaid.run();
    } catch (error) {
      console.error('Mermaid theme update failed:', error);
    }
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initMermaid);
} else {
  initMermaid();
}
