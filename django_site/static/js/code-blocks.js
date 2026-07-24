/**
 * Copy and collapse for Hugo-style code blocks (.code-block-container).
 */
(function () {
  const ICON_COPY =
    '<svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">' +
    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" ' +
    'd="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>';
  const ICON_CHECK =
    '<svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">' +
    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>';
  const ICON_CHEVRON_UP =
    '<svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">' +
    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>';
  const ICON_CHEVRON_DOWN =
    '<svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">' +
    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>';

  const lang = document.documentElement.lang?.startsWith('pt') ? 'pt' : 'en';
  const i18n = {
    en: {
      copy: 'Copy',
      copied: 'Copied!',
      selected: 'Selected',
      collapse: 'Collapse',
      expand: 'Expand',
      collapseTitle: 'Collapse code',
      expandTitle: 'Expand code',
      clickToExpand: 'Click to expand',
    },
    pt: {
      copy: 'Copiar',
      copied: 'Copiado!',
      selected: 'Selecionado',
      collapse: 'Recolher',
      expand: 'Expandir',
      collapseTitle: 'Recolher código',
      expandTitle: 'Expandir código',
      clickToExpand: 'Clique para expandir',
    },
  };
  const t = i18n[lang] || i18n.en;

  function getCodeText(container) {
    const codeTableCell = container.querySelector('.lntd:last-child code');
    if (codeTableCell) {
      return (codeTableCell.textContent || '').trim();
    }

    const codeElement = container.querySelector('code');
    if (codeElement) {
      const hasInlineLineNumbers = codeElement.querySelector('.ln');
      if (hasInlineLineNumbers) {
        const codeLines = codeElement.querySelectorAll('.cl');
        if (codeLines.length > 0) {
          return Array.from(codeLines)
            .map((line) => (line.textContent || '').replace(/\n+$/, ''))
            .join('\n')
            .replace(/\n+$/, '')
            .trim();
        }
      }
      return (codeElement.textContent || '').trim();
    }

    return (container.textContent || '').trim();
  }

  async function handleCopy(btn) {
    const codeId = btn.dataset.codeId;
    const container = document.getElementById(codeId);
    if (!container) return;

    const copyIcon = btn.querySelector('.copy-icon');
    const copyText = btn.querySelector('.copy-text');

    try {
      await navigator.clipboard.writeText(getCodeText(container));
      if (copyIcon) copyIcon.innerHTML = ICON_CHECK;
      if (copyText) copyText.textContent = t.copied;
      btn.classList.add('text-green-600');
      setTimeout(() => {
        if (copyIcon) copyIcon.innerHTML = ICON_COPY;
        if (copyText) copyText.textContent = t.copy;
        btn.classList.remove('text-green-600');
      }, 2000);
    } catch {
      const codeElement = container.querySelector('code') || container;
      const range = document.createRange();
      range.selectNodeContents(codeElement);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      if (copyText) copyText.textContent = t.selected;
      setTimeout(() => {
        if (copyText) copyText.textContent = t.copy;
        selection.removeAllRanges();
      }, 2000);
    }
  }

  function initCollapse(btn) {
    const codeId = btn.dataset.codeId;
    const container = document.getElementById(codeId);
    if (!container || btn.dataset.collapseInit === '1') return;
    btn.dataset.collapseInit = '1';

    const collapseIcon = btn.querySelector('.collapse-icon');
    const collapseText = btn.querySelector('.collapse-text');
    const overlay = container.querySelector('.collapse-overlay');
    const overlayLabel = overlay?.querySelector('div');
    if (overlayLabel) overlayLabel.textContent = t.clickToExpand;

    let codeElement = container.querySelector('pre.chroma') || container.querySelector('pre');
    const defaultState = btn.dataset.defaultState || 'expanded';
    const autoCollapseLines = parseInt(btn.dataset.autoCollapseLines, 10) || 30;
    const autoCollapseHeight = parseInt(btn.dataset.autoCollapseHeight, 10) || 400;
    const collapsedHeight = parseInt(btn.dataset.collapsedHeight, 10) || 120;
    let isCollapsed = false;

    function shouldAutoCollapse() {
      if (codeElement) {
        const lines = codeElement.querySelectorAll('.line, .cl');
        const height = codeElement.offsetHeight;
        if (lines.length > autoCollapseLines || height > autoCollapseHeight) return true;
      }
      if (container.offsetHeight > autoCollapseHeight) return true;
      const textContent = container.textContent || '';
      return textContent.split('\n').length > autoCollapseLines;
    }

    function setCollapsed(collapsed) {
      if (!overlay) return;
      isCollapsed = collapsed;
      if (collapsed) {
        container.style.maxHeight = collapsedHeight + 'px';
        container.style.overflow = 'hidden';
        overlay.style.opacity = '1';
        overlay.style.pointerEvents = 'auto';
        if (collapseIcon) collapseIcon.innerHTML = ICON_CHEVRON_DOWN;
        if (collapseText) collapseText.textContent = t.expand;
        btn.title = t.expandTitle;
        btn.setAttribute('aria-label', t.expandTitle);
      } else {
        container.style.maxHeight = '';
        container.style.overflow = '';
        overlay.style.opacity = '0';
        overlay.style.pointerEvents = 'none';
        if (collapseIcon) collapseIcon.innerHTML = ICON_CHEVRON_UP;
        if (collapseText) collapseText.textContent = t.collapse;
        btn.title = t.collapseTitle;
        btn.setAttribute('aria-label', t.collapseTitle);
      }
    }

    if (btn.dataset.collapsed === 'true' || defaultState === 'collapsed' || shouldAutoCollapse()) {
      setCollapsed(true);
    }

    btn.addEventListener('click', () => setCollapsed(!isCollapsed));
    overlay?.addEventListener('click', () => {
      if (isCollapsed) setCollapsed(false);
    });
  }

  function localizeButtons() {
    document.querySelectorAll('.copy-code-btn .copy-text').forEach((el) => {
      el.textContent = t.copy;
    });
    document.querySelectorAll('.collapse-code-btn .collapse-text').forEach((el) => {
      el.textContent = t.collapse;
    });
  }

  document.addEventListener('click', (e) => {
    const copyBtn = e.target.closest('.copy-code-btn');
    if (copyBtn) {
      e.preventDefault();
      handleCopy(copyBtn);
      return;
    }
    const collapseBtn = e.target.closest('.collapse-code-btn');
    if (collapseBtn) {
      e.preventDefault();
    }
  });

  function init() {
    localizeButtons();
    document.querySelectorAll('.collapse-code-btn').forEach(initCollapse);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
