"""YouTube RSS fetch + cached home page data."""
import json
import logging
import re
from datetime import datetime, timezone as dt_tz

import feedparser
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

_VIDEO_ID_RE = re.compile(
    r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
)


def is_youtube_short(entry) -> bool:
    """Return True for YouTube Shorts entries in channel RSS."""
    link = (getattr(entry, 'link', '') or '').lower()
    if '/shorts/' in link:
        return True
    title = (getattr(entry, 'title', '') or '').lower()
    return '#short' in title


def is_long_form_video(video: dict) -> bool:
    """Return True when a cached/parsed video dict is not a Short."""
    watch_url = (video.get('watch_url') or '').lower()
    if '/shorts/' in watch_url:
        return False
    title = (video.get('title') or '').lower()
    return '#short' not in title


def extract_video_id(entry) -> str:
    """Resolve YouTube video ID from a feedparser entry."""
    video_id = getattr(entry, 'yt_videoid', None)
    if video_id:
        return video_id

    entry_id = getattr(entry, 'id', '') or ''
    if entry_id.startswith('yt:video:'):
        return entry_id.split(':', 2)[-1]

    link = getattr(entry, 'link', '') or ''
    match = _VIDEO_ID_RE.search(link)
    if match:
        return match.group(1)

    return ''


def _entry_published_iso(entry) -> str:
    published_parsed = getattr(entry, 'published_parsed', None)
    if published_parsed:
        dt = datetime(*published_parsed[:6], tzinfo=dt_tz.utc)
        return dt.isoformat()
    return getattr(entry, 'published', '') or ''


def _entry_description(entry) -> str:
    for attr in ('media_description', 'summary', 'description'):
        value = getattr(entry, attr, '') or ''
        if value:
            return re.sub(r'\s+', ' ', value).strip()[:500]
    return ''


def parse_youtube_entry(entry) -> dict | None:
    """Convert one RSS entry into the home template video dict."""
    if is_youtube_short(entry):
        return None

    video_id = extract_video_id(entry)
    if not video_id:
        return None

    watch_url = f'https://www.youtube.com/watch?v={video_id}'
    return {
        'id': video_id,
        'title': getattr(entry, 'title', '')[:255],
        'description': _entry_description(entry),
        'published_at': _entry_published_iso(entry),
        'thumbnail': f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg',
        'embed_url': f'https://www.youtube.com/embed/{video_id}',
        'watch_url': watch_url,
    }


def fetch_youtube_rss(channel_id: str | None = None, limit: int = 4) -> dict:
    """Fetch recent videos from YouTube channel RSS."""
    channel_id = channel_id or settings.YOUTUBE_CHANNEL_ID
    if not channel_id:
        raise ValueError('No YouTube channel_id configured')

    url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()

    parsed = feedparser.parse(resp.content)
    recent_videos = []
    max_scan = max(limit * 5, 25)
    for entry in parsed.entries[:max_scan]:
        video = parse_youtube_entry(entry)
        if video:
            recent_videos.append(video)
        if len(recent_videos) >= limit:
            break

    return {
        'recent_videos': recent_videos,
        'last_updated': datetime.now(dt_tz.utc).isoformat(),
        'total_videos': len(recent_videos),
        'source': 'rss_feed',
    }


def _load_youtube_json_file() -> dict:
    path = settings.BASE_DIR / 'data' / 'youtube.json'
    if not path.exists():
        return {}
    with path.open(encoding='utf-8') as handle:
        return json.load(handle)


def get_youtube_data(limit: int = 4) -> dict:
    """Return YouTube data for the home page (cache → RSS → static file)."""
    from integrations.models import IntegrationConfig

    config = IntegrationConfig.objects.filter(provider='youtube', is_active=True).first()
    if config:
        cached = (config.config_json or {}).get('recent_videos') or []
        if cached:
            long_form = [v for v in cached if is_long_form_video(v)]
            return {
                'recent_videos': long_form[:limit],
                'last_updated': (config.config_json or {}).get('last_updated'),
                'total_videos': len(long_form),
                'source': (config.config_json or {}).get('source', 'integration_cache'),
            }

    try:
        return fetch_youtube_rss(limit=limit)
    except Exception as exc:
        logger.warning('Live YouTube RSS fetch failed: %s', exc)

    return _load_youtube_json_file()
