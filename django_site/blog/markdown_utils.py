"""Shared markdown rendering for posts."""
import re

import bleach
import markdown
from django.conf import settings
from django.utils.safestring import mark_safe

from .code_blocks import enhance_code_blocks


def _bleach_tags():
    return getattr(settings, 'BLEACH_ALLOWED_TAGS', [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'p', 'br', 'hr',
        'ul', 'ol', 'li',
        'blockquote', 'pre', 'code',
        'a', 'strong', 'em', 'del', 's',
        'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'img', 'div', 'span',
    ])


def _bleach_attributes():
    return getattr(settings, 'BLEACH_ALLOWED_ATTRIBUTES', {
        '*': ['class', 'id'],
        'a': ['href', 'title', 'rel', 'target'],
        'img': ['src', 'alt', 'title', 'class', 'loading'],
        'code': ['class'],
        'pre': ['class'],
        'div': ['class'],
        'span': ['class'],
        'th': ['align'],
        'td': ['align'],
    })


def _prepare_markdown(text):
    """Convert Hugo shortcodes before markdown parsing."""
    if not text:
        return ''

    text = re.sub(
        r'```asciinema\s*\n([a-zA-Z0-9_-]+)\s*\n```',
        r'<div class="asciinema-embed my-6 not-prose">'
        r'<script src="https://asciinema.org/a/\1/embed" async></script></div>',
        text,
    )
    text = re.sub(
        r'\{\{<\s*mermaid\s*>\}\}(.*?)\{\{<\s*/\s*mermaid\s*>\}\}',
        lambda match: f'\n```mermaid\n{match.group(1).strip()}\n```\n',
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'\{\{<\s*asciinema\s+([a-zA-Z0-9_-]+)\s*>\}\}',
        r'<div class="asciinema-embed my-6 not-prose">'
        r'<script src="https://asciinema.org/a/\1/embed" async></script></div>',
        text,
    )
    return re.sub(
        r'\{\{<\s*youtube\s+([a-zA-Z0-9_-]+)\s*>\}\}',
        r'<div class="youtube-embed aspect-video my-6 overflow-hidden rounded-lg bg-muted">'
        r'<a href="https://www.youtube.com/watch?v=\1" target="_blank" rel="noopener noreferrer" '
        r'class="block w-full h-full relative group">'
        r'<img src="https://i.ytimg.com/vi/\1/hqdefault.jpg" alt="YouTube video" '
        r'class="w-full h-full object-cover" loading="lazy" />'
        r'<div class="absolute inset-0 flex items-center justify-center bg-black/30 '
        r'group-hover:bg-black/50 transition-colors">'
        r'<svg class="w-16 h-16 text-white opacity-90 group-hover:opacity-100" '
        r'fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>'
        r'</div></a></div>',
        text,
    )


def _markdown_instance():
    extensions = [
        ext for ext in getattr(settings, 'MARKDOWN_EXTENSIONS', [
            'markdown.extensions.extra',
            'markdown.extensions.toc',
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
        ])
        if ext != 'markdown.extensions.codehilite'
    ]
    return markdown.Markdown(
        extensions=extensions,
        extension_configs={
            'markdown.extensions.toc': {
                'permalink': False,
            },
        },
    )


def _sanitize(html):
    allowed_protocols = tuple(bleach.sanitizer.ALLOWED_PROTOCOLS) + ('mailto',)
    return bleach.clean(
        html,
        tags=_bleach_tags(),
        attributes=_bleach_attributes(),
        protocols=allowed_protocols,
        strip=True,
        strip_comments=True,
    )


def render_markdown(text):
    """Return sanitized HTML and optional table of contents."""
    prepared = _prepare_markdown(text)
    md = _markdown_instance()
    html = md.convert(prepared)
    html = enhance_code_blocks(html)
    toc = md.toc or ''
    return mark_safe(_sanitize(html)), mark_safe(_sanitize(toc)) if toc else ''


def plain_text(text, max_length=500):
    """Strip markdown/HTML for search index snippets."""
    prepared = _prepare_markdown(text or '')
    md = _markdown_instance()
    html = md.convert(prepared)
    plain = bleach.clean(html, tags=[], strip=True)
    plain = re.sub(r'\s+', ' ', plain).strip()
    if max_length and len(plain) > max_length:
        return plain[:max_length]
    return plain
