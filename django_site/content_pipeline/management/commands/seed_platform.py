from django.core.management.base import BaseCommand

from curation.models import FeedSource
from integrations.models import IntegrationConfig


DEFAULT_FEEDS = [
    ('Kubernetes Blog', 'https://kubernetes.io/feed.xml'),
    ('CNCF', 'https://www.cncf.io/feed/'),
    ('Google Cloud Blog', 'https://cloud.google.com/blog/topics/devops-prod-professionals/rss'),
    ('HashiCorp', 'https://www.hashicorp.com/blog/feed.xml'),
    ('Matheus Blog', 'https://matheusthurler.com.br/index.xml'),
]

YOUTUBE_CHANNEL_ID = 'UCHVZvp_RfNpwfATmQ-NaDyw'


class Command(BaseCommand):
    help = 'Seed default feed sources and integration configs'

    def handle(self, *args, **options):
        for name, url in DEFAULT_FEEDS:
            FeedSource.objects.get_or_create(name=name, defaults={'url': url})
        for provider in ('youtube', 'github'):
            IntegrationConfig.objects.get_or_create(provider=provider, defaults={'is_active': True})
        yt, _ = IntegrationConfig.objects.get_or_create(provider='youtube')
        yt.config_json = {**yt.config_json, 'channel_id': YOUTUBE_CHANNEL_ID}
        yt.save(update_fields=['config_json'])
        self.stdout.write(self.style.SUCCESS('Platform defaults seeded'))
