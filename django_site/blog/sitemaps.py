"""Sitemap for blog."""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Post


class PostSitemap(Sitemap):
    """Sitemap for blog posts."""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Post.objects.published()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages."""
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return ['blog:home', 'blog:post_list', 'blog:about',
                'blog:category_list', 'blog:tag_list', 'blog:archives',
                'blog:privacy', 'blog:terms']

    def location(self, item):
        return reverse(item)
