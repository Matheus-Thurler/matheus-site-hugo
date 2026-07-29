"""Page caching and CDN-friendly Cache-Control for public blog views."""

from __future__ import annotations

from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.utils.cache import patch_cache_control
from django.views.decorators.cache import cache_page

# Paths that receive public CDN cache headers (admin/auth excluded).
PUBLIC_CACHE_PREFIXES = (
    '/posts/',
    '/categories/',
    '/tags/',
    '/archives/',
    '/about/',
    '/links/',
    '/privacy/',
    '/terms/',
    '/series/',
    '/start-here/',
    '/projects/',
    '/pages/',
)

PUBLIC_CACHE_EXACT = ('/', '/pt/', '/pt')


def _is_public_cache_path(path: str) -> bool:
    if path.startswith(('/admin/', '/accounts/', '/newsletter/api/', '/analytics/', '/discord/', '/internal/')):
        return False
    if path in PUBLIC_CACHE_EXACT:
        return True
    if path.startswith('/pt/'):
        stripped = path[3:]
        if stripped in ('', '/'):
            return True
        return any(stripped.startswith(prefix) for prefix in PUBLIC_CACHE_PREFIXES)
    return any(path.startswith(prefix) for prefix in PUBLIC_CACHE_PREFIXES)


def patch_public_cache_control(response):
    """Apply CDN-friendly Cache-Control for Firebase Hosting edge cache."""
    max_age = getattr(settings, 'PUBLIC_CACHE_MAX_AGE', 300)
    s_maxage = getattr(settings, 'PUBLIC_CACHE_S_MAXAGE', 3600)
    patch_cache_control(
        response,
        public=True,
        max_age=max_age,
        s_maxage=s_maxage,
        stale_while_revalidate=86400,
    )
    response['Vary'] = 'Accept-Language'
    return response


def public_cache_page(timeout=None):
    """Cache full GET responses for anonymous visitors."""
    timeout = timeout if timeout is not None else getattr(settings, 'CACHE_PAGE_TIMEOUT', 900)

    def decorator(view_func):
        cached_view = cache_page(timeout)(view_func)

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method != 'GET':
                return view_func(request, *args, **kwargs)
            if getattr(request.user, 'is_authenticated', False):
                response = view_func(request, *args, **kwargs)
                return patch_public_cache_control(response)
            response = cached_view(request, *args, **kwargs)
            return patch_public_cache_control(response)

        return wrapper

    return decorator


def method_public_cache_page(timeout=None):
    """Class-based view helper — use with @method_decorator(..., name='dispatch')."""
    return public_cache_page(timeout)


def invalidate_public_cache():
    """Clear page cache after content changes."""
    cache.clear()


class PublicCacheMiddleware:
    """Add Cache-Control headers on public HTML even when view is not cache_page-wrapped."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method != 'GET' or response.status_code != 200:
            return response
        content_type = response.get('Content-Type', '')
        if 'text/html' not in content_type:
            return response
        if getattr(request.user, 'is_authenticated', False):
            return response
        if not _is_public_cache_path(request.path):
            return response
        if 'Cache-Control' not in response:
            patch_public_cache_control(response)
        return response
