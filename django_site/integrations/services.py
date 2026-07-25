"""YouTube + GitHub sync integrations."""
import logging

from django.conf import settings
from django.utils import timezone

from integrations.youtube import fetch_youtube_rss

logger = logging.getLogger(__name__)


def sync_youtube(config, dry_run=False):
    """Fetch latest videos from YouTube channel RSS and cache for the home page."""
    channel_id = (config.config_json or {}).get('channel_id') or settings.YOUTUBE_CHANNEL_ID
    if not channel_id:
        return {'error': 'No channel_id configured'}

    data = fetch_youtube_rss(channel_id=channel_id, limit=5)
    if not dry_run:
        config.config_json = {
            **(config.config_json or {}),
            'channel_id': channel_id,
            'recent_videos': data['recent_videos'],
            'last_updated': timezone.now().isoformat(),
            'total_videos': data['total_videos'],
            'source': data['source'],
        }
        config.last_sync_at = timezone.now()
        config.last_result = f"{len(data['recent_videos'])} videos"
        config.save(update_fields=['config_json', 'last_sync_at', 'last_result'])
    return data


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
