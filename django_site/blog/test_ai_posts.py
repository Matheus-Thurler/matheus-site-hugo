import json
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from blog.ai_posts import _unique_slug, create_draft_post, generate_post_payload
from blog.models import Author, Post


SAMPLE_PAYLOAD = {
    'slug': 'ansible-cloudstack',
    'title_en': 'Install CloudStack with Ansible',
    'description_en': 'A practical guide.',
    'content_en': '## Intro\n\nRun `ansible-playbook`.',
    'title_pt': 'Instale CloudStack com Ansible',
    'description_pt': 'Guia prático.',
    'content_pt': '## Intro\n\nRode `ansible-playbook`.',
    'keywords': 'ansible, cloudstack',
    'tags': ['ansible', 'cloudstack'],
    'category': 'automation',
}


@override_settings(GEMINI_API_KEY='test-key', GEMINI_MODEL='gemini-3.5-flash')
class GeneratePostPayloadTests(TestCase):
    @patch('google.genai.Client')
    def test_generate_post_payload_parses_json(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.text = json.dumps(SAMPLE_PAYLOAD)
        mock_client_cls.return_value.models.generate_content.return_value = mock_response

        payload = generate_post_payload('Brief about ansible')

        self.assertEqual(payload['slug'], 'ansible-cloudstack')
        self.assertIn('ansible-playbook', payload['content_en'])

    def test_missing_api_key_raises(self):
        with self.settings(GEMINI_API_KEY=''):
            with self.assertRaises(RuntimeError):
                generate_post_payload('test')


class CreateDraftPostTests(TestCase):
    def test_create_draft_post(self):
        post = create_draft_post(SAMPLE_PAYLOAD, brief='original brief')
        self.assertEqual(post.status, 'draft')
        self.assertEqual(post.slug, 'ansible-cloudstack')
        self.assertEqual(post.tags.count(), 2)
        self.assertEqual(post.category.slug, 'automation')

    def test_unique_slug_when_collision(self):
        author = Author.objects.create(name='Test', slug='test-author')
        Post.objects.create(
            author=author,
            slug='ansible-cloudstack',
            status='draft',
            title_en='Existing',
        )
        slug = _unique_slug('ansible-cloudstack')
        self.assertEqual(slug, 'ansible-cloudstack-2')
