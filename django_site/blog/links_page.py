"""Helpers for the /links/ link-in-bio page."""

from django.conf import settings
from django.urls import NoReverseMatch, reverse


def _resolve_link_url(item):
    internal_route = getattr(item, 'internal_route', '') or ''
    if internal_route:
        try:
            return reverse(internal_route)
        except NoReverseMatch:
            pass
    return item.url


def _localized(item, lang, field_base):
    if lang == 'pt':
        value = getattr(item, f'{field_base}_pt', '') or ''
        if value:
            return value
    return getattr(item, f'{field_base}_en', '') or ''


def _settings_card_links(lang):
    from django.urls import reverse

    raw_links = settings.LINKS_PAGE_PT if lang == 'pt' else settings.LINKS_PAGE_EN
    page_links = []
    for item in raw_links:
        link = dict(item)
        if 'url_name' in link:
            link['url'] = reverse(link.pop('url_name'))
        page_links.append(link)
    return page_links


def get_card_links(lang):
    """Main link cards for /links/ (DB first, settings fallback)."""
    from blog.models import ProfileLink

    qs = ProfileLink.objects.filter(is_active=True, section=ProfileLink.SECTION_CARD)
    if not qs.exists():
        return _settings_card_links(lang)

    page_links = []
    for item in qs:
        entry = {
            'title': _localized(item, lang, 'title'),
            'description': _localized(item, lang, 'description'),
            'url': _resolve_link_url(item),
            'external': item.external,
        }
        if item.image:
            entry['image'] = item.image
        elif item.icon:
            entry['icon'] = item.icon
        page_links.append(entry)
    return page_links


def get_social_links():
    """Social icon row for /links/ (DB first, settings fallback)."""
    from blog.models import ProfileLink

    qs = ProfileLink.objects.filter(is_active=True, section=ProfileLink.SECTION_SOCIAL)
    if not qs.exists():
        return settings.AUTHOR_SOCIAL

    social_links = []
    for item in qs:
        social_links.append({
            'name': item.title_en or item.title_pt or item.icon,
            'url': _resolve_link_url(item),
            'icon': item.icon,
        })
    return social_links
