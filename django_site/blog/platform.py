"""Platform features: search, AI tools, YouTube matching, status, changelog, projects."""
import json
import logging
import re
from datetime import timedelta
from pathlib import Path

import requests
from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone

logger = logging.getLogger(__name__)


def search_posts(query: str, limit: int = 50):
    """Full-text search with PostgreSQL, icontains fallback on SQLite."""
    from blog.models import Post

    query = (query or '').strip()
    if not query:
        return Post.objects.none()

    base = Post.objects.published()
    if getattr(settings, 'DB_ENGINE', 'sqlite') == 'postgresql':
        try:
            from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

            vector = SearchVector(
                'title_en', 'title_pt',
                'description_en', 'description_pt',
                'content_en', 'content_pt',
            )
            search_query = SearchQuery(query)
            return (
                base.annotate(search=vector, rank=SearchRank(vector, search_query))
                .filter(search=search_query)
                .order_by('-rank')[:limit]
            )
        except Exception as exc:
            logger.warning('PostgreSQL search failed, using fallback: %s', exc)

    q = Q(title_en__icontains=query) | Q(title_pt__icontains=query)
    q |= Q(description_en__icontains=query) | Q(description_pt__icontains=query)
    q |= Q(content_en__icontains=query) | Q(content_pt__icontains=query)
    return base.filter(q).distinct()[:limit]


def analytics_dashboard_stats(days: int = 7):
    """Aggregate stats for admin analytics dashboard."""
    from analytics.models import PageView
    from blog.models import PostFeedback

    since = timezone.now() - timedelta(days=days)
    views = PageView.objects.filter(created_at__gte=since)
    top_posts = (
        views.exclude(post_slug='')
        .values('post_slug')
        .annotate(views=Count('id'))
        .order_by('-views')[:10]
    )
    top_paths = (
        views.values('path')
        .annotate(views=Count('id'))
        .order_by('-views')[:10]
    )
    referrers = (
        views.exclude(referrer='')
        .values('referrer')
        .annotate(views=Count('id'))
        .order_by('-views')[:10]
    )
    feedback = (
        PostFeedback.objects.filter(created_at__gte=since)
        .values('helpful')
        .annotate(count=Count('id'))
    )
    return {
        'days': days,
        'total_views': views.count(),
        'unique_visitors': views.values('visitor_hash').distinct().count(),
        'top_posts': list(top_posts),
        'top_paths': list(top_paths),
        'top_referrers': list(referrers),
        'feedback': {row['helpful']: row['count'] for row in feedback},
    }


def match_youtube_videos_to_posts():
    """Suggest YouTube video IDs for posts based on title/slug overlap."""
    from blog.models import Post
    from integrations.youtube import get_youtube_data

    data = get_youtube_data(limit=20)
    videos = data.get('recent_videos') or []
    suggestions = []
    for post in Post.objects.published().filter(youtube_video_id=''):
        title = (post.get_title() or '').lower()
        slug = post.slug.lower()
        for video in videos:
            vtitle = (video.get('title') or '').lower()
            vid = video.get('id', '')
            if not vid:
                continue
            slug_words = [w for w in slug.split('-') if len(w) > 3]
            if slug.replace('-', ' ') in vtitle or any(w in vtitle for w in slug_words):
                suggestions.append({
                    'post': post,
                    'post_slug': post.slug,
                    'video_id': vid,
                    'video_title': video.get('title', ''),
                    'watch_url': video.get('watch_url', ''),
                })
                break
            if any(word in title for word in slug_words[:3] if word in vtitle):
                suggestions.append({
                    'post': post,
                    'post_slug': post.slug,
                    'video_id': vid,
                    'video_title': video.get('title', ''),
                    'watch_url': video.get('watch_url', ''),
                })
                break
    return suggestions


def fetch_github_projects(username: str | None = None, limit: int = 12) -> list[dict]:
    """Fetch public GitHub repos for the projects page."""
    username = username or getattr(settings, 'GITHUB_USERNAME', 'Matheus-Thurler')
    url = f'https://api.github.com/users/{username}/repos'
    params = {'sort': 'updated', 'per_page': limit, 'type': 'owner'}
    headers = {'Accept': 'application/vnd.github+json'}
    token = getattr(settings, 'GITHUB_TOKEN', '')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        repos = []
        for repo in resp.json():
            if repo.get('fork'):
                continue
            repos.append({
                'name': repo.get('name', ''),
                'description': repo.get('description') or '',
                'url': repo.get('html_url', ''),
                'stars': repo.get('stargazers_count', 0),
                'language': repo.get('language') or '',
                'updated_at': repo.get('updated_at', ''),
            })
        return repos
    except Exception as exc:
        logger.warning('GitHub projects fetch failed: %s', exc)
        return []


def get_projects_data() -> list[dict]:
    from integrations.models import IntegrationConfig

    config = IntegrationConfig.objects.filter(provider='github', is_active=True).first()
    cached = (config.config_json or {}).get('projects') if config else None
    if cached:
        return cached
    return fetch_github_projects()


def sync_github_projects(config, dry_run=False):
    projects = fetch_github_projects()
    if not dry_run and config:
        config.config_json = {**(config.config_json or {}), 'projects': projects}
        config.last_sync_at = timezone.now()
        config.last_result = f'{len(projects)} repos'
        config.save(update_fields=['config_json', 'last_sync_at', 'last_result'])
    return {'projects': projects}


def check_homelab_status() -> list[dict]:
    """HTTP health checks for homelab status page."""
    checks = getattr(settings, 'HOMELAB_STATUS_CHECKS', [])
    results = []
    for item in checks:
        name = item.get('name', 'Service')
        url = item.get('url', '')
        if not url:
            continue
        status = 'unknown'
        detail = ''
        try:
            resp = requests.get(url, timeout=10)
            status = 'up' if resp.status_code < 400 else 'down'
            detail = str(resp.status_code)
        except Exception as exc:
            status = 'down'
            detail = str(exc)[:120]
        results.append({'name': name, 'url': url, 'status': status, 'detail': detail})
    return results


def parse_changelog(max_entries: int = 30) -> list[dict]:
    """Parse CHANGELOG.md into structured entries."""
    path = Path(getattr(settings, 'CHANGELOG_PATH', settings.BASE_DIR.parent / 'CHANGELOG.md'))
    if not path.exists():
        return []
    entries = []
    current = None
    for line in path.read_text(encoding='utf-8').splitlines():
        version_match = re.match(r'^## \[?([^\]]+)\]?\s*-?\s*(.*)$', line)
        if version_match:
            if current:
                entries.append(current)
            current = {
                'version': version_match.group(1).strip(),
                'date': version_match.group(2).strip(),
                'items': [],
            }
            continue
        if current and line.strip().startswith('- '):
            current['items'].append(line.strip()[2:])
    if current:
        entries.append(current)
    return entries[:max_entries]


def get_start_here_posts(lang='en'):
    from blog.models import Post

    slugs = getattr(settings, 'START_HERE_POST_SLUGS', [])
    if not slugs:
        return Post.objects.published().order_by('-published_at')[:5]
    posts = []
    for slug in slugs:
        slug = slug.strip()
        if not slug:
            continue
        post = Post.objects.published().filter(slug=slug).first()
        if post:
            posts.append(post)
    return posts


def ask_post_question(post, question: str, lang='en') -> str:
    """RAG-lite: answer using post content via Gemini."""
    from google import genai

    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        raise ValueError('GEMINI_API_KEY is not configured')
    content = post.get_content(lang)[:12000]
    client = genai.Client(api_key=api_key)
    model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')
    prompt = (
        'Answer ONLY based on the blog post below. '
        'If the answer is not in the post, say you do not know.\n\n'
        f'Post title: {post.get_title(lang)}\n\n'
        f'Post content:\n{content}\n\n'
        f'Question: {question}'
    )
    response = client.models.generate_content(model=model, contents=prompt)
    return (response.text or '').strip()


def translate_post_with_ai(post, target_lang: str) -> dict:
    """Translate missing post fields to target_lang (en or pt)."""
    from google import genai

    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        raise ValueError('GEMINI_API_KEY is not configured')
    source_lang = 'pt' if target_lang == 'en' else 'en'
    payload = {
        'title': post.get_title(source_lang),
        'description': post.get_description(source_lang),
        'content': post.get_content(source_lang),
    }
    client = genai.Client(api_key=api_key)
    model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')
    prompt = (
        f'Translate this blog post from {source_lang} to {target_lang}. '
        'Keep Markdown formatting. Return ONLY JSON: '
        '{"title":"","description":"","content":""}\n\n'
        f'{json.dumps(payload, ensure_ascii=False)}'
    )
    response = client.models.generate_content(model=model, contents=prompt)
    text = (response.text or '').strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[-1].rsplit('```', 1)[0].strip()
    return json.loads(text)


def generate_seo_meta(post, lang='both') -> dict:
    """Generate OG/SEO meta fields with Gemini."""
    from google import genai

    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        raise ValueError('GEMINI_API_KEY is not configured')
    client = genai.Client(api_key=api_key)
    model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')
    brief = {
        'title_en': post.title_en,
        'title_pt': post.title_pt,
        'description_en': post.description_en[:500],
        'description_pt': post.description_pt[:500],
    }
    prompt = (
        'Generate SEO meta for a DevOps blog post. Return ONLY JSON:\n'
        '{"og_title_en":"","og_title_pt":"","og_description_en":"","og_description_pt":"",'
        '"keywords":""}\n\n'
        f'Post:\n{json.dumps(brief, ensure_ascii=False)}'
    )
    response = client.models.generate_content(model=model, contents=prompt)
    text = (response.text or '').strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[-1].rsplit('```', 1)[0].strip()
    return json.loads(text)


def generate_crosspost_drafts(post, lang='en') -> dict:
    """Generate social cross-post drafts for a published post."""
    from google import genai

    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        raise ValueError('GEMINI_API_KEY is not configured')
    client = genai.Client(api_key=api_key)
    model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')
    prompt = (
        'Write social media drafts for a DevOps blog post. Return ONLY JSON:\n'
        '{"linkedin":"","mastodon":"","telegram":""}\n'
        'Keep each under platform limits. Include post URL placeholder {url}.\n\n'
        f'Title: {post.get_title(lang)}\n'
        f'Description: {post.get_description(lang)[:400]}'
    )
    response = client.models.generate_content(model=model, contents=prompt)
    text = (response.text or '').strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[-1].rsplit('```', 1)[0].strip()
    return json.loads(text)


def moderate_comment_with_ai(comment) -> dict:
    """Score comment for spam/toxicity. Returns {approve: bool, reason: str}."""
    from google import genai

    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        return {'approve': True, 'reason': 'AI not configured'}
    client = genai.Client(api_key=api_key)
    model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')
    prompt = (
        'Moderate this blog comment. Return ONLY JSON: '
        '{"approve": true/false, "reason": "short reason"}\n'
        'Reject spam, scams, hate, or off-topic content.\n\n'
        f'Comment:\n{comment.content[:2000]}'
    )
    response = client.models.generate_content(model=model, contents=prompt)
    text = (response.text or '').strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[-1].rsplit('```', 1)[0].strip()
    return json.loads(text)
