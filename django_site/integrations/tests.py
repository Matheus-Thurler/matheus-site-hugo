from django.test import SimpleTestCase

from integrations.youtube import extract_video_id, parse_youtube_entry


class YouTubeParserTests(SimpleTestCase):
    def test_extract_video_id_from_watch_url(self):
        entry = type('Entry', (), {
            'link': 'https://www.youtube.com/watch?v=abc123XYZ_-',
            'id': '',
        })()
        self.assertEqual(extract_video_id(entry), 'abc123XYZ_-')

    def test_parse_youtube_entry_builds_home_fields(self):
        entry = type('Entry', (), {
            'title': 'Demo video',
            'link': 'https://www.youtube.com/watch?v=abc123XYZ_-',
            'id': 'yt:video:abc123XYZ_-',
            'published_parsed': (2026, 1, 15, 12, 0, 0),
            'summary': 'Short description',
        })()
        video = parse_youtube_entry(entry)
        self.assertEqual(video['id'], 'abc123XYZ_-')
        self.assertEqual(video['watch_url'], entry.link)
        self.assertIn('hqdefault.jpg', video['thumbnail'])
        self.assertIn('/embed/', video['embed_url'])
