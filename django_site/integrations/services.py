"""YouTube + GitHub sync integrations."""
import logging

from django.conf import settings
from django.utils import timezone

from integrations.youtube import fetch_youtube_rss

logger = logging.getLogger(__name__)


def sync_github_projects(config, dry_run=False):
    from blog.platform import sync_github_projects as _sync_projects

    return _sync_projects(config, dry_run=dry_run)


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


def sync_github(config, dry_run=False):
    """Sync Hugo posts and GitHub projects cache."""
    if dry_run:
        from blog.platform import fetch_github_projects
        return {'dry_run': True, 'projects': fetch_github_projects()}
    from django.core.management import call_command
    from django.utils import timezone

    call_command('update_hugo_posts')
    project_result = sync_github_projects(config, dry_run=False)
    config.last_sync_at = timezone.now()
    config.last_result = f"update_hugo_posts OK; {project_result.get('projects', []) and len(project_result['projects'])} repos"
    config.save(update_fields=['last_sync_at', 'last_result'])
    return {'status': 'ok', **project_result}


def sync_github_posts(config, dry_run=False):
    """Backward-compatible alias."""
    return sync_github(config, dry_run=dry_run)


def sync_all(dry_run=False):
    from .models import IntegrationConfig

    results = {}
    for config in IntegrationConfig.objects.filter(is_active=True):
        try:
            if config.provider == 'youtube':
                results['youtube'] = sync_youtube(config, dry_run=dry_run)
            elif config.provider == 'github':
                results['github'] = sync_github(config, dry_run=dry_run)
        except Exception as exc:
            logger.exception('Sync failed for %s', config.provider)
            results[config.provider] = {'error': str(exc)}
    return results
