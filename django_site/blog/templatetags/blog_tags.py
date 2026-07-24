"""Custom template tags for blog app."""
import re

from django import template
from django.utils.safestring import mark_safe

from blog.markdown_utils import render_markdown

register = template.Library()


@register.filter
def markdown_format(text):
    """Convert markdown text to HTML with XSS protection."""
    html, _toc = render_markdown(text)
    return html


@register.simple_tag(takes_context=True)
def nav_link_classes(context, url_name, *args, **kwargs):
    """Return Hugo-style nav classes with active indicator."""
    from django.urls import reverse, NoReverseMatch

    request = context.get('request')
    if not request:
        return 'nav-link text-muted-foreground hover:text-primary hover:bg-primary/10 focus:ring-primary/20 relative flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all duration-300 ease-out hover:-translate-y-0.5 hover:scale-105 focus:ring-2 focus:outline-none'

    try:
        target = reverse(url_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return 'nav-link text-muted-foreground hover:text-primary hover:bg-primary/10 focus:ring-primary/20 relative flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all duration-300 ease-out hover:-translate-y-0.5 hover:scale-105 focus:ring-2 focus:outline-none'

    current = request.path.rstrip('/') or '/'
    target = target.rstrip('/') or '/'
    is_active = current == target or current.startswith(f'{target}/')

    if is_active:
        return (
            'nav-link nav-active-indicator bg-accent text-accent-foreground '
            'focus:ring-primary/20 relative flex items-center gap-2 rounded-lg px-4 py-2 '
            'text-sm font-medium transition-all duration-300 ease-out hover:-translate-y-0.5 '
            'hover:scale-105 focus:ring-2 focus:outline-none'
        )
    return (
        'nav-link text-muted-foreground hover:text-primary hover:bg-primary/10 '
        'focus:ring-primary/20 relative flex items-center gap-2 rounded-lg px-4 py-2 '
        'text-sm font-medium transition-all duration-300 ease-out hover:-translate-y-0.5 '
        'hover:scale-105 focus:ring-2 focus:outline-none'
    )


@register.filter
def truncatewords_html(text, length):
    """Truncate text by words, preserving HTML tags."""
    if not text:
        return ""

    import re
    plain = re.sub(r'<[^>]+>', '', text)
    words = plain.split()

    if len(words) <= length:
        return text

    truncated = ' '.join(words[:length]) + '...'
    return truncated
