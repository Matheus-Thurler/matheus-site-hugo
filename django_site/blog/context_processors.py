"""Context processors for blog app."""
from django.urls import reverse


def _resolve_footer_menu(lang):
    from django.conf import settings

    items = settings.FOOTER_MENU_PT if lang == 'pt' else settings.FOOTER_MENU_EN
    resolved = []
    for item in items:
        entry = {'name': item['name'], 'external': item.get('external', False)}
        if 'url_name' in item:
            entry['url'] = reverse(item['url_name'])
        else:
            entry['url'] = item['url']
        resolved.append(entry)
    return resolved


def site_settings(request):
    """Add site settings to all templates."""
    from django.conf import settings
    from django.utils.translation import get_language

    lang = get_language()
    if lang not in ('en', 'pt'):
        lang = 'en'

    return {
        'lang': lang,
        'site_name': settings.SITE_NAME,
        'site_description': settings.SITE_DESCRIPTION,
        'site_keywords': settings.SITE_KEYWORDS,
        'author_name': settings.AUTHOR_NAME,
        'author_title': settings.AUTHOR_TITLE,
        'author_description': settings.AUTHOR_DESCRIPTION,
        'author_github': settings.AUTHOR_GITHUB,
        'author_youtube': settings.AUTHOR_YOUTUBE,
        'author_linkedin': settings.AUTHOR_LINKEDIN,
        'author_email': settings.AUTHOR_EMAIL,
        'show_theme_switch': settings.SHOW_THEME_SWITCH,
        'show_dark_mode_switch': settings.SHOW_DARK_MODE_SWITCH,
        'show_language_switch': settings.SHOW_LANGUAGE_SWITCH,
        'show_dock': settings.SHOW_DOCK,
        'sticky_header': settings.STICKY_HEADER,
        'footer_menu': _resolve_footer_menu(lang),
        'language_switch_mode': settings.LANGUAGE_SWITCH_MODE,
        'color_scheme': settings.COLOR_SCHEME,
        'default_color_mode': settings.DEFAULT_COLOR_MODE,
        'dock_mode': settings.DOCK_MODE,
        'recent_posts_count': settings.RECENT_POSTS_COUNT,
        'related_posts_count': settings.RELATED_POSTS_COUNT,
        'newsletter_subscribe_url': settings.NEWSLETTER_SUBSCRIBE_URL or reverse('newsletter:subscribe'),
        'comments_enabled': settings.COMMENTS_ENABLED,
        'analytics_enabled': settings.ANALYTICS_ENABLED,
        'analytics_self_hosted': getattr(settings, 'ANALYTICS_SELF_HOSTED', True),
        'google_analytics_id': settings.GOOGLE_ANALYTICS_ID,
        'google_adsense_id': settings.GOOGLE_ADSENSE_ID,
        'google_adsense_client_id': settings.adsense_client_id(),
        'google_adsense_slot': settings.GOOGLE_ADSENSE_SLOT,
        'reading_progress_enabled': settings.READING_PROGRESS_ENABLED,
        'reading_progress_height': settings.READING_PROGRESS_HEIGHT,
        'giscus_repo': settings.GISCUS_REPO,
        'giscus_repo_id': settings.GISCUS_REPO_ID,
        'giscus_category': settings.GISCUS_CATEGORY,
        'giscus_category_id': settings.GISCUS_CATEGORY_ID,
        'giscus_mapping': settings.GISCUS_MAPPING,
        'giscus_reactions_enabled': settings.GISCUS_REACTIONS_ENABLED,
        'giscus_emit_metadata': settings.GISCUS_EMIT_METADATA,
        'giscus_input_position': settings.GISCUS_INPUT_POSITION,
        'giscus_theme': settings.GISCUS_THEME,
    }
