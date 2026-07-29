from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from blog.models import Author, Category, Post


class PublicCacheHeadersTest(TestCase):
    def setUp(self):
        author = Author.objects.create(name='Test Author', slug='test-author')
        category = Category.objects.create(name='DevOps', slug='devops')
        self.post = Post.objects.create(
            slug='cache-test-post',
            status='published',
            title_en='Cache Test',
            content_en='# Hello\n\nCached content.',
            author=author,
            category=category,
            published_at=timezone.now(),
        )
        self.client = Client()

    def test_home_has_public_cache_control(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        cache_control = response['Cache-Control']
        self.assertIn('public', cache_control)
        self.assertIn('s-maxage', cache_control)

    def test_post_detail_has_public_cache_control(self):
        response = self.client.get(f'/posts/{self.post.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('public', response['Cache-Control'])

    def test_authenticated_user_skips_page_cache(self):
        user = User.objects.create_user('reader', password='secret')
        self.client.force_login(user)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('public', response['Cache-Control'])

    @override_settings(CACHE_PAGE_TIMEOUT=60)
    def test_post_detail_is_cached_for_anonymous(self):
        url = f'/posts/{self.post.slug}/'
        first = self.client.get(url)
        second = self.client.get(url)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.content, second.content)


class PrerenderCommandTest(TestCase):
    def setUp(self):
        author = Author.objects.create(name='Author', slug='author')
        Post.objects.create(
            slug='prerender-me',
            status='published',
            title_en='Prerender',
            content_en='Body',
            author=author,
            published_at=timezone.now(),
        )

    def test_prerender_writes_index_html_with_canonical_urls(self):
        from io import StringIO
        import shutil

        from django.conf import settings
        from django.core.management import call_command

        output = settings.PRERENDER_OUTPUT_DIR / '_test_prerender'
        if output.exists():
            shutil.rmtree(output)

        out = StringIO()
        call_command(
            'prerender_pages',
            output=str(output),
            host=settings.SITE_CANONICAL_HOST,
            stdout=out,
        )
        target = output / 'posts' / 'prerender-me' / 'index.html'
        self.assertTrue(target.exists())
        html = target.read_text()
        self.assertIn('Prerender', html)
        self.assertIn(settings.SITE_CANONICAL_URL, html)
        self.assertNotIn('localhost', html)
        shutil.rmtree(output)
