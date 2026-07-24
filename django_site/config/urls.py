"""URL configuration for Matheus Thurler Blog."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from blog.sitemaps import PostSitemap, StaticViewSitemap
from blog.views import robots_txt, search_index
from blog.feeds import LatestPostsFeed
from config.admin_docs import ADMIN_HOME_INTRO, APP_SECTIONS

_admin_index = admin.site.index


def _admin_index_with_docs(request, extra_context=None):
    extra_context = extra_context or {}
    extra_context['admin_home_intro'] = ADMIN_HOME_INTRO
    extra_context['admin_app_sections'] = APP_SECTIONS
    return _admin_index(request, extra_context)


admin.site.index = _admin_index_with_docs

sitemaps = {
    'posts': PostSitemap,
    'static': StaticViewSitemap,
}

# Non-translatable URLs
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include('allauth.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('index.json', search_index, name='search_index'),
    path('index.xml', LatestPostsFeed(), name='rss_feed'),
    path('llms.txt', TemplateView.as_view(template_name='llms.txt', content_type='text/plain')),
    path('newsletter/', include('newsletter.urls')),
    path('analytics/', include('analytics.urls')),
    path('discord/', include('discord_bot.urls')),
    path('internal/scheduler/', include('content_pipeline.urls')),
]

# Translatable URLs (PT prefix when language is pt)
urlpatterns += i18n_patterns(
    path('', include('blog.urls')),
    prefix_default_language=False,
)

# Serve media + static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Production: serve static files via APP
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
