"""RSS feed matching Hugo /index.xml."""
from django.contrib.syndication.views import Feed
from django.conf import settings

from .models import Post


class LatestPostsFeed(Feed):
    title = settings.SITE_NAME
    link = '/'
    description = settings.SITE_DESCRIPTION

    def items(self):
        return Post.objects.published()[:20]

    def item_title(self, item):
        return item.get_title()

    def item_description(self, item):
        return item.get_description()

    def item_link(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        return item.published_at
