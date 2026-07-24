"""Enhance fenced code blocks with Chroma highlighting and Hugo-style copy UI."""
import html as html_module
import re

from django.conf import settings
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name, guess_lexer

FENCED_CODE_RE = re.compile(
    r'<pre><code(?: class="language-([^"]+)")?>(.*?)</code></pre>',
    re.DOTALL | re.IGNORECASE,
)

CODEHILITE_RE = re.compile(
    r'<div class="codehilite"><pre><span></span><code>(.*?)</code></pre></div>',
    re.DOTALL | re.IGNORECASE,
)

_CHROMA_FORMATTER = HtmlFormatter(cssclass='chroma', linenos=False, nowrap=False)

_ICON_CODE = (
    '<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">'
    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" '
    'd="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg>'
)
_ICON_COPY = (
    '<svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">'
    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" '
    'd="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>'
)
_ICON_CHEVRON_UP = (
    '<svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">'
    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>'
)


def _highlight_code(code: str, lang: str | None) -> str:
    try:
        lexer = get_lexer_by_name(lang) if lang else TextLexer()
    except Exception:
        try:
            lexer = guess_lexer(code)
        except Exception:
            lexer = TextLexer()
    return highlight(code.rstrip('\n') + '\n', lexer, _CHROMA_FORMATTER)


def _wrap_codeblock(chroma_html: str, lang: str | None, code_id: str) -> str:
    display_lang = html_module.escape((lang or 'text').upper())
    collapse_enabled = getattr(settings, 'CODEBLOCK_COLLAPSE_ENABLED', True)
    default_state = getattr(settings, 'CODEBLOCK_COLLAPSE_DEFAULT', 'expanded')
    auto_lines = getattr(settings, 'CODEBLOCK_AUTO_COLLAPSE_LINES', 30)
    auto_height = getattr(settings, 'CODEBLOCK_AUTO_COLLAPSE_HEIGHT', 400)
    collapsed_height = getattr(settings, 'CODEBLOCK_COLLAPSED_HEIGHT', 120)

    collapse_btn = ''
    collapse_overlay = ''
    if collapse_enabled:
        collapse_btn = f'''
      <button type="button"
        class="collapse-code-btn text-muted-foreground hover:text-primary hover:bg-primary/10 focus:ring-primary/20 flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium transition-all duration-200 ease-out focus:ring-2 focus:outline-none"
        data-code-id="{code_id}"
        data-default-state="{default_state}"
        data-collapsed="false"
        data-auto-collapse-lines="{auto_lines}"
        data-auto-collapse-height="{auto_height}"
        data-collapsed-height="{collapsed_height}"
        title="Collapse code"
        aria-label="Collapse code">
        <span class="collapse-icon">{_ICON_CHEVRON_UP}</span>
        <span class="collapse-text hidden sm:inline">Collapse</span>
      </button>'''
        collapse_overlay = '''
    <div class="collapse-overlay to-card/90 pointer-events-none absolute inset-0 bg-gradient-to-b from-transparent via-transparent opacity-0 transition-opacity duration-300">
      <div class="text-muted-foreground bg-card/80 border-border/50 hover:bg-primary/10 hover:text-primary hover:border-primary/30 absolute bottom-4 left-1/2 -translate-x-1/2 cursor-pointer rounded-full border px-3 py-1.5 text-xs backdrop-blur-sm transition-all duration-200">
        Click to expand
      </div>
    </div>'''

    return f'''<div class="code-block-container border-border bg-card my-6 overflow-hidden rounded-xl border shadow-sm transition-all duration-200 ease-out hover:-translate-y-0.5 hover:shadow-md not-prose">
  <div class="code-block-header bg-muted/30 border-border flex items-center justify-between border-b px-4 py-3">
    <div class="flex items-center gap-2">
      <div class="text-muted-foreground flex-shrink-0">{_ICON_CODE}</div>
      <span class="text-muted-foreground text-sm font-medium">{display_lang}</span>
    </div>
    <div class="flex items-center gap-2">{collapse_btn}
      <button type="button"
        class="copy-code-btn text-muted-foreground hover:text-primary hover:bg-primary/10 focus:ring-primary/20 flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium transition-all duration-200 ease-out focus:ring-2 focus:outline-none"
        data-code-id="{code_id}"
        title="Copy code"
        aria-label="Copy code">
        <span class="copy-icon">{_ICON_COPY}</span>
        <span class="copy-text hidden sm:inline">Copy</span>
      </button>
    </div>
  </div>
  <div class="code-block-content relative" id="{code_id}">
    {chroma_html}{collapse_overlay}
  </div>
</div>'''


def enhance_code_blocks(html: str) -> str:
    """Replace markdown code blocks with Chroma-highlighted blocks + copy button."""
    counter = {'n': 0}

    def replace_fenced(match):
        lang = match.group(1)
        raw_code = html_module.unescape(match.group(2))
        code_id = f'code-{counter["n"]}'
        counter['n'] += 1
        chroma = _highlight_code(raw_code, lang)
        return _wrap_codeblock(chroma, lang, code_id)

    def replace_codehilite(match):
        raw_code = html_module.unescape(match.group(1))
        # Strip pygments span tags to get plain text for re-highlighting
        plain = re.sub(r'<[^>]+>', '', raw_code)
        code_id = f'code-{counter["n"]}'
        counter['n'] += 1
        chroma = _highlight_code(plain, None)
        return _wrap_codeblock(chroma, None, code_id)

    html = FENCED_CODE_RE.sub(replace_fenced, html)
    html = CODEHILITE_RE.sub(replace_codehilite, html)
    return html
