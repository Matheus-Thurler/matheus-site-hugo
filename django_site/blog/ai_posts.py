"""Generate blog post drafts with Google Gemini."""
import json
import re
from typing import Any

from django.conf import settings
from django.utils.text import slugify

SYSTEM_PROMPT = """You are a technical blog writer for Matheus Thurler's DevOps & Cloud blog.
Audience: engineers working with GCP, Kubernetes, Terraform, CI/CD, homelab, and platform engineering.
Tone: direct, practical, friendly PT-BR / EN as requested. No fluff.

Output ONLY valid JSON (no markdown fences) with this schema:
{
  "slug": "kebab-case-url-slug",
  "title_en": "English title",
  "description_en": "1-2 sentence SEO description in English",
  "content_en": "Full post body in Markdown (English). Use ## headings, lists, fenced code blocks when useful.",
  "title_pt": "Portuguese title",
  "description_pt": "1-2 sentence SEO description in Portuguese",
  "content_pt": "Full post body in Markdown (Portuguese)",
  "keywords": "comma, separated, keywords",
  "tags": ["tag1", "tag2"],
  "category": "single category slug-like name e.g. devops, kubernetes, automation"
}

Rules:
- Markdown only in content fields (no HTML).
- Include practical examples or commands when the brief mentions implementation.
- slug must be lowercase ASCII kebab-case, max 80 chars.
- tags: 3-6 lowercase items, no # prefix.
"""


def _language_instruction(language: str) -> str:
    if language == 'en':
        return 'Generate English content only. Duplicate EN title/description/content into PT fields as empty strings.'
    if language == 'pt':
        return 'Generate Portuguese (pt-BR) content only. Leave EN title/description/content as empty strings.'
    return 'Generate both English and Portuguese versions with equivalent meaning.'


def build_prompt(brief: str, language: str, include_code: bool) -> str:
    code_note = (
        'Include at least one fenced code block with a realistic example.'
        if include_code
        else 'Use code blocks only if clearly needed.'
    )
    return (
        f"{_language_instruction(language)}\n"
        f"{code_note}\n\n"
        f"Author brief — expand into a complete blog post draft:\n\n{brief.strip()}"
    )


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
    return json.loads(text)


def _unique_slug(base_slug: str, exclude_pk=None) -> str:
    from blog.models import Post

    slug = slugify(base_slug)[:80] or 'draft-post'
    candidate = slug
    n = 2
    while Post.objects.filter(slug=candidate).exclude(pk=exclude_pk).exists():
        suffix = f'-{n}'
        candidate = f'{slug[: 80 - len(suffix)]}{suffix}'
        n += 1
    return candidate


def generate_post_payload(
    brief: str,
    *,
    language: str = 'both',
    include_code: bool = True,
) -> dict[str, Any]:
    """Call Gemini and return parsed post fields."""
    api_key = getattr(settings, 'GEMINI_API_KEY', '') or ''
    if not api_key:
        raise RuntimeError(
            'GEMINI_API_KEY is not configured. Set it in the environment or .env file.'
        )

    from google import genai

    model = getattr(settings, 'GEMINI_MODEL', 'gemini-3.5-flash')
    client = genai.Client(api_key=api_key)
    prompt = build_prompt(brief, language, include_code)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            'system_instruction': SYSTEM_PROMPT,
            'response_mime_type': 'application/json',
            'temperature': 0.7,
        },
    )

    raw = (response.text or '').strip()
    if not raw:
        raise RuntimeError('Gemini returned an empty response.')

    data = _extract_json(raw)
    required = ('slug', 'title_en', 'content_en', 'title_pt', 'content_pt')
    for key in required:
        if key not in data:
            raise RuntimeError(f'Gemini response missing field: {key}')

    data['slug'] = _unique_slug(data.get('slug') or data.get('title_en') or 'draft')
    return data


def create_draft_post(payload: dict[str, Any], *, brief: str = '') -> 'Post':
    """Persist Gemini output as a draft Post."""
    from django.conf import settings as dj_settings
    from blog.models import Author, Category, Post, Tag

    author, _ = Author.objects.get_or_create(
        slug='matheus-thurler',
        defaults={
            'name': dj_settings.AUTHOR_NAME,
            'title': dj_settings.AUTHOR_TITLE,
            'description': dj_settings.AUTHOR_DESCRIPTION,
        },
    )

    category = None
    cat_name = (payload.get('category') or '').strip()
    if cat_name:
        cat_slug = slugify(cat_name)[:100] or 'general'
        category, _ = Category.objects.get_or_create(
            slug=cat_slug,
            defaults={'name': cat_name.title()},
        )

    post = Post.objects.create(
        author=author,
        category=category,
        slug=payload['slug'],
        status='draft',
        title_en=(payload.get('title_en') or '').strip(),
        description_en=(payload.get('description_en') or '').strip(),
        content_en=(payload.get('content_en') or '').strip(),
        title_pt=(payload.get('title_pt') or '').strip(),
        description_pt=(payload.get('description_pt') or '').strip(),
        content_pt=(payload.get('content_pt') or '').strip(),
        keywords=(payload.get('keywords') or '').strip(),
    )

    for tag_name in payload.get('tags') or []:
        name = str(tag_name).strip().lstrip('#').lower()
        if not name:
            continue
        tag_slug = slugify(name)[:100] or name
        tag, _ = Tag.objects.get_or_create(slug=tag_slug, defaults={'name': name})
        post.tags.add(tag)

    if brief:
        post.keywords = post.keywords or brief[:500]

    post.save()
    return post
