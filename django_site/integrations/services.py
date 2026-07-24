"""YouTube + GitHub sync integrations."""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def sync_youtube(config, dry_run=False):
    """Fetch latest videos from YouTube channel RSS."""
    channel_id = config.config_json.get('channel_id') or settings.YOUTUBE_CHANNEL_ID
    if not channel_id:
        return {'error': 'No channel_id configured'}
    url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    import feedparser
    parsed = feedparser.parse(resp.content)
    videos = [
        {'title': e.title, 'url': e.link}
        for e in parsed.entries[:5]
    ]
    if not dry_run:
        config.last_sync_at = __import__('django.utils.timezone', fromlist=['timezone']).timezone.now()
        config.last_result = str(len(videos)) + ' videos'
        config.save(update_fields=['last_sync_at', 'last_result'])
    return {'videos': videos}


def sync_github_posts(config, dry_run=False):
    """Trigger Hugo post update from repo content."""
    if dry_run:
        return {'dry_run': True}
    from django.core.management import call_command
    from django.utils import timezone

    call_command('update_hugo_posts')
    config.last_sync_at = timezone.now()
    config.last_result = 'update_hugo_posts OK'
    config.save(update_fields=['last_sync_at', 'last_result'])
    return {'status': 'ok'}


def sync_all(dry_run=False):
    from .models import IntegrationConfig

    results = {}
    for config in IntegrationConfig.objects.filter(is_active=True):
        try:
            if config.provider == 'youtube':
                results['youtube'] = sync_youtube(config, dry_run=dry_run)
            elif config.provider == 'github':
                results['github'] = sync_github_posts(config, dry_run=dry_run)
        except Exception as exc:
            logger.exception('Sync failed for %s', config.provider)
            results[config.provider] = {'error': str(exc)}
    return results
