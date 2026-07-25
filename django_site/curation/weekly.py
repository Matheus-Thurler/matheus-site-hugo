"""Weekly newsletter curation — Gemini draft + Discord review (content-automation parity)."""
import logging
from datetime import datetime, timedelta, timezone as dt_tz

import feedparser
from django.conf import settings
from google import genai

logger = logging.getLogger(__name__)

GEMINI_PROMPT = """
Você é um assistente de curadoria de conteúdo para uma newsletter de DevOps & Cloud em PT-BR.

Aqui estão os conteúdos da semana:

## Meu conteúdo publicado:
{my_content}

## Novidades da comunidade:
{community_content}

Crie um draft de newsletter seguindo este formato:
1. Destaque do meu conteúdo (1 item principal)
2. Top 3-5 novidades da comunidade (resumo de 1 linha cada)
3. Uma dica rápida prática (comando, config, ou atalho)

Regras:
- Escreva em PT-BR natural
- Seja direto e técnico
- Máximo 400 palavras
- Tom: amigável mas profissional
- Links DEVEM usar formato markdown: [título](url)
- NÃO use headers markdown (##). Use **negrito** para seções
- Use bullet points (- ) para listas
"""

COMMUNITY_SOURCES = {
    'gcp_releases': 'https://cloud.google.com/feeds/gcp-release-notes.xml',
    'kubernetes_blog': 'https://kubernetes.io/feed.xml',
    'hashicorp_blog': 'https://www.hashicorp.com/blog/feed.xml',
}


def _fetch_my_content():
    items = []
    channel_id = settings.YOUTUBE_CHANNEL_ID
    if channel_id:
        feed = feedparser.parse(f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}')
        from integrations.youtube import extract_video_id, is_youtube_short

        video_count = 0
        for entry in feed.entries[:15]:
            if is_youtube_short(entry):
                continue
            video_id = getattr(entry, 'yt_videoid', '') or extract_video_id(entry)
            if not video_id:
                continue
            items.append(f'- [Vídeo] {entry.title}: https://www.youtube.com/watch?v={video_id}')
            video_count += 1
            if video_count >= 3:
                break

    blog_url = getattr(settings, 'BLOG_RSS_URL', 'https://matheusthurler.com.br/index.xml')
    feed = feedparser.parse(blog_url)
    for entry in feed.entries[:3]:
        items.append(f'- [Post] {entry.title}: {entry.link}')

    return '\n'.join(items) if items else 'Nenhum conteúdo novo esta semana.'


def _fetch_community_content():
    items = []
    for source_name, url in COMMUNITY_SOURCES.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                items.append(f'- [{source_name}] {entry.title}: {entry.link}')
        except Exception as exc:
            logger.warning('Feed error %s: %s', source_name, exc)
    return '\n'.join(items) if items else 'Nenhuma novidade encontrada.'


def generate_weekly_draft_text() -> str:
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError('GEMINI_API_KEY is not configured')
    client = genai.Client(api_key=api_key)
    prompt = GEMINI_PROMPT.format(
        my_content=_fetch_my_content(),
        community_content=_fetch_community_content(),
    )
    response = client.models.generate_content(
        model=getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash'),
        contents=prompt,
    )
    return (response.text or '').strip()


def run_weekly_curation(*, post_to_discord=True):
    """
    Generate weekly newsletter draft, save as Campaign, post to Discord #drafts-review.
    Returns the NewsletterCampaign instance.
    """
    from campaigns.models import NewsletterCampaign
    from discord_bot.client import post_draft_for_review

    draft_text = generate_weekly_draft_text()
    today = datetime.now(dt_tz.utc).strftime('%Y-%m-%d')
    campaign = NewsletterCampaign.objects.create(
        subject_en=f'Newsletter {today}',
        subject_pt=f'Newsletter {today}',
        body_markdown=draft_text,
        status='pending_review',
    )

    if post_to_discord:
        msg = post_draft_for_review(campaign)
        campaign.discord_message_id = str(msg['id'])
        campaign.discord_channel_id = str(msg.get('channel_id', settings.DISCORD_DRAFTS_CHANNEL_ID))
        campaign.save(update_fields=['discord_message_id', 'discord_channel_id'])

    return campaign


def check_new_content(hours=24):
    """Daily check — new blog posts / YouTube videos in last N hours."""
    cutoff = datetime.now(dt_tz.utc) - timedelta(hours=hours)
    new_items = []

    channel_id = settings.YOUTUBE_CHANNEL_ID
    if channel_id:
        from integrations.youtube import extract_video_id, is_youtube_short

        feed = feedparser.parse(f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}')
        for entry in feed.entries[:15]:
            if is_youtube_short(entry):
                continue
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=dt_tz.utc)
                if published > cutoff:
                    video_id = getattr(entry, 'yt_videoid', '') or extract_video_id(entry)
                    new_items.append({
                        'type': 'video',
                        'title': entry.title,
                        'url': f'https://www.youtube.com/watch?v={video_id}',
                    })

    blog_url = getattr(settings, 'BLOG_RSS_URL', 'https://matheusthurler.com.br/index.xml')
    feed = feedparser.parse(blog_url)
    for entry in feed.entries[:5]:
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6], tzinfo=dt_tz.utc)
            if published > cutoff:
                new_items.append({
                    'type': 'post',
                    'title': entry.title,
                    'url': entry.link,
                })

    return new_items


def run_daily_content_check(*, post_to_discord=True):
    """Post new content to Discord newsletter channel if any found."""
    from discord_bot.client import post_new_content_items

    items = check_new_content()
    if items and post_to_discord:
        post_new_content_items(items)
    return items
