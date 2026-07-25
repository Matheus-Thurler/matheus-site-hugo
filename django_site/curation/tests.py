from django.test import TestCase, override_settings

from curation.models import CuratedItem, FeedSource
from curation.services import create_post_draft

SQLITE_SETTINGS = {
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
}


@override_settings(**SQLITE_SETTINGS)
class CuratedDraftTests(TestCase):
    def test_create_post_draft_links_curated_item(self):
        source = FeedSource.objects.create(
            name='Test feed',
            url='https://example.com/feed.xml',
        )
        item = CuratedItem.objects.create(
            source=source,
            title='Kubernetes Gateway API updates',
            url='https://example.com/gateway-api',
            ai_summary='Useful summary for platform engineers.',
            tags='kubernetes,gateway-api',
            status='approved',
        )

        post = create_post_draft(item)
        item.refresh_from_db()

        self.assertEqual(post.status, 'draft')
        self.assertEqual(item.post_id, post.id)
        self.assertIn('Gateway API updates', post.title_en)
        self.assertEqual(post.tags.count(), 2)

    def test_create_post_draft_is_idempotent(self):
        source = FeedSource.objects.create(
            name='Test feed',
            url='https://example.com/feed-2.xml',
        )
        item = CuratedItem.objects.create(
            source=source,
            title='Another item',
            url='https://example.com/another-item',
            status='approved',
        )

        first = create_post_draft(item)
        second = create_post_draft(item)
        self.assertEqual(first.id, second.id)
