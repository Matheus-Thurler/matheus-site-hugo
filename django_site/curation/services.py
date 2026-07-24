"""RSS curation + Gemini summarization + Discord notifications."""
import json
import logging
from datetime import datetime, timezone as dt_tz

import feedparser
import requests
from django.conf import settings
from google import genai

logger = logging.getLogger(__name__)


def _gemini_client():
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        raise ValueError('GEMINI_API_KEY is not configured.')
    return genai.Client(api_key=api_key)


def fetch_feed_entries(source):
    """Return list of dicts from RSS/Atom feed."""
    parsed = feedparser.parse(source.url)
    entries = []
    for entry in parsed.entries[: source.max_items]:
        published = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6], tzinfo=dt_tz.utc)
        entries.append({
            'title': getattr(entry, 'title', '')[:500],
            'url': getattr(entry, 'link', ''),
            'summary': getattr(entry, 'summary', '')[:2000],
            'published_at': published,
        })
    return entries


def summarize_with_gemini(items: list[dict]) -> list[dict]:
    """Score and summarize feed items for DevOps relevance."""
    if not items:
        return []
    client = _gemini_client()
    model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')
    brief = json.dumps(items[:20], default=str)
    prompt = (
        'You curate a DevOps/Cloud/Kubernetes newsletter. '
        'Given RSS items as JSON, return ONLY valid JSON array:\n'
        '[{"title","url","summary":"2 sentences","score":0-100,"tags":["..."]}]\n'
        'Pick top relevant items, score by practical value for platform engineers.\n\n'
        f'Items:\n{brief}'
    )
    response = client.models.generate_content(model=model, contents=prompt)
    text = (response.text or '').strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[-1].rsplit('```', 1)[0].strip()
    return json.loads(text)


def notify_discord(message: str, items: list | None = None):
    """Post curation results to Discord (#drafts-review via bot, or webhook)."""
    webhook = getattr(settings, 'DISCORD_WEBHOOK_URL', '')
    token = getattr(settings, 'DISCORD_BOT_TOKEN', '')
    channel_id = getattr(settings, 'DISCORD_DRAFTS_CHANNEL_ID', '')

    embeds = []
    for item in (items or [])[:5]:
        embeds.append({
            'title': item.get('title', '')[:256],
            'url': item.get('url', ''),
            'description': item.get('summary', '')[:300],
        })
    payload = {'content': message[:2000], 'embeds': embeds}

    if token and channel_id:
        headers = {
            'Authorization': f'Bot {token}',
            'Content-Type': 'application/json',
        }
        url = f'https://discord.com/api/v10/channels/{channel_id}/messages'
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        return

    if webhook:
        requests.post(webhook, json=payload, timeout=15)
        return

    logger.info('Discord not configured — set DISCORD_BOT_TOKEN or DISCORD_WEBHOOK_URL')


def run_curation(dry_run=False):
    """Fetch all active feeds, dedupe, summarize, persist CuratedItems."""
    from .models import CuratedItem, FeedSource

    created = 0
    all_new = []
    for source in FeedSource.objects.filter(is_active=True):
        for entry in fetch_feed_entries(source):
            if CuratedItem.objects.filter(url=entry['url']).exists():
                continue
            if dry_run:
                all_new.append(entry)
                continue
            item = CuratedItem.objects.create(
                source=source,
                title=entry['title'],
                url=entry['url'],
                raw_summary=entry.get('summary', ''),
                published_at=entry.get('published_at'),
                status='pending',
            )
            all_new.append({'title': item.title, 'url': item.url, 'summary': item.raw_summary[:200]})
            created += 1

    if all_new and getattr(settings, 'GEMINI_API_KEY', ''):
        try:
            ranked = summarize_with_gemini(all_new)
            for rank in ranked:
                CuratedItem.objects.filter(url=rank.get('url')).update(
                    ai_summary=rank.get('summary', ''),
                    score=rank.get('score', 0),
                    tags=','.join(rank.get('tags', [])),
                )
            notify_discord(
                f'📰 Curation: {len(all_new)} new items',
                ranked if ranked else all_new,
            )
        except Exception as exc:
            logger.exception('Gemini curation failed: %s', exc)

    return created
