"""Instagram carousel generation — portado de instagram-automation (Go)."""

from __future__ import annotations

import json
import re
import unicodedata

TEMPLATE_META = {
    'cheatsheet': {'badge': 'Cheatsheet', 'gradient': '160deg, #0a1628 0%, #0d2137 30%, #0f2b4a 60%, #0a1628 100%'},
    'tip': {'badge': 'Dica', 'gradient': '160deg, #1a0a28 0%, #2d1245 30%, #1a0a28 60%, #0f0618 100%'},
    'comparison': {'badge': 'Comparativo', 'gradient': '160deg, #0f172a 0%, #1e1b4b 40%, #312e81 70%, #0f172a 100%'},
}

CTA_KEYWORDS = ('salva', 'compartilha', 'segue', 'siga', 'curta', 'comenta', 'save', 'share', 'follow')

TECH_LOGOS: dict[str, dict[str, object]] = {
    'kustomize': {
        'name': 'Kustomize',
        'file': 'images/tech-logos/kustomize.svg',
        'aliases': ('kustomize', 'kustomization'),
    },
    'argocd': {
        'name': 'Argo CD',
        'file': 'images/tech-logos/argocd.svg',
        'aliases': ('argocd', 'argo cd', 'argo'),
    },
    'kubernetes': {
        'name': 'Kubernetes',
        'file': 'images/tech-logos/kubernetes.svg',
        'aliases': ('kubernetes', 'k8s', 'kubectl'),
    },
    'helm': {
        'name': 'Helm',
        'file': 'images/tech-logos/helm.svg',
        'aliases': ('helm',),
    },
    'nginx': {
        'name': 'Nginx',
        'file': 'images/tech-logos/nginx.svg',
        'aliases': ('nginx',),
    },
    'traefik': {
        'name': 'Traefik',
        'file': 'images/tech-logos/traefik.svg',
        'aliases': ('traefik', 'traefik proxy'),
    },
    'docker': {
        'name': 'Docker',
        'file': 'images/tech-logos/docker.svg',
        'aliases': ('docker',),
    },
    'github': {
        'name': 'GitHub',
        'file': 'images/tech-logos/github.svg',
        'aliases': ('github', 'github actions'),
    },
    'terraform': {
        'name': 'Terraform',
        'file': 'images/tech-logos/terraform.svg',
        'aliases': ('terraform', 'tf', 'opentofu'),
    },
}

_LOGO_MATCHERS: list[tuple[str, str]] = sorted(
    ((alias, slug) for slug, meta in TECH_LOGOS.items() for alias in meta['aliases']),
    key=lambda item: len(item[0]),
    reverse=True,
)


def _normalize_text(value: str) -> str:
    value = unicodedata.normalize('NFKD', value or '')
    value = value.encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'\s+', ' ', value.lower()).strip()


def _match_logo_slug(text: str) -> str | None:
    normalized = _normalize_text(text)
    if not normalized:
        return None
    for alias, slug in _LOGO_MATCHERS:
        if alias in normalized:
            return slug
    return None


def _leading_logo_slug(text: str) -> str | None:
    normalized = _normalize_text(text)
    if not normalized:
        return None
    head = re.split(r'[:?,!;]', normalized, maxsplit=1)[0].strip()
    if not head:
        return None
    slug = _match_logo_slug(head)
    if slug:
        return slug
    first_token = head.split()[0]
    return _match_logo_slug(first_token)


def resolve_cover_logos(*, topic: str = '', title: str = '', post_type: str = '') -> list[dict[str, object]]:
    """Resolve logos reais a partir do título/tópico (ex.: Kustomize vs Argo CD)."""
    combined = _normalize_text(f'{title} {topic}')
    if not combined:
        return []

    for separator in (r'\s+vs\.?\s+', r'\s+x\s+', r'\s+versus\s+'):
        parts = re.split(separator, combined, maxsplit=1)
        if len(parts) == 2:
            logos: list[dict[str, object]] = []
            seen: set[str] = set()
            for part in parts:
                slug = _leading_logo_slug(part)
                if slug and slug not in seen:
                    seen.add(slug)
                    meta = TECH_LOGOS[slug]
                    logos.append({
                        'slug': slug,
                        'name': meta['name'],
                        'file': meta['file'],
                    })
            if len(logos) >= 2:
                return logos

    entre_match = re.search(r'entre\s+([a-z0-9 .-]+?)\s+e\s+([a-z0-9 .-]+)', combined)
    if entre_match:
        logos = []
        seen: set[str] = set()
        for part in entre_match.groups():
            slug = _leading_logo_slug(part)
            if slug and slug not in seen:
                seen.add(slug)
                meta = TECH_LOGOS[slug]
                logos.append({
                    'slug': slug,
                    'name': meta['name'],
                    'file': meta['file'],
                })
        if len(logos) >= 2:
            return logos

    slug = _match_logo_slug(combined)
    if slug:
        meta = TECH_LOGOS[slug]
        return [{
            'slug': slug,
            'name': meta['name'],
            'file': meta['file'],
        }]
    return []


TOPIC_KEY_STOPWORDS = (
    'qual a diferenca',
    'diferencas entre',
    'diferenca entre',
    'como funciona',
    'guia',
    'tutorial',
    'introducao',
    'o que e',
)


def normalize_topic_key(*, topic: str = '', title: str = '') -> str:
    """Chave normalizada para evitar carrosséis duplicados sobre o mesmo assunto."""
    text = _normalize_text(topic or title)
    if not text:
        return ''
    for phrase in TOPIC_KEY_STOPWORDS:
        text = text.replace(phrase, ' ')
    text = re.sub(r'[^\w\s-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return ''

    for separator in (r'\s+vs\.?\s+', r'\s+x\s+', r'\s+versus\s+'):
        parts = re.split(separator, text, maxsplit=1)
        if len(parts) == 2:
            left = parts[0].strip()
            right = parts[1].strip()
            if left and right:
                return ' vs '.join(sorted([left, right]))[:255]

    entre_match = re.search(r'entre\s+([a-z0-9-]+)\s+e\s+([a-z0-9-]+)', text)
    if entre_match:
        left = entre_match.group(1).strip()
        right = entre_match.group(2).strip()
        if left and right:
            return ' vs '.join(sorted([left, right]))[:255]

    e_match = re.search(r'^([a-z0-9-]+)\s+e\s+([a-z0-9-]+)', text)
    if e_match:
        left = e_match.group(1).strip()
        right = e_match.group(2).strip()
        if left and right:
            return ' vs '.join(sorted([left, right]))[:255]

    return text[:255]


def find_duplicate_carousel(*, topic: str = '', title: str = '', exclude_pk: int | None = None):
    from content_pipeline.models import InstagramCarousel

    key = normalize_topic_key(topic=topic, title=title)
    if not key:
        return None
    qs = InstagramCarousel.objects.filter(topic_key=key)
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    return qs.first()


def reorder_slides(slides: list[dict]) -> list[dict]:
    """Garante ordem cover → conteúdo → CTA (mesma lógica do instagen Go)."""
    if len(slides) < 3:
        return slides

    def is_cta(slide: dict) -> bool:
        heading = (slide.get('heading') or '').lower()
        body = (slide.get('body') or '').lower()
        if any(kw in heading for kw in CTA_KEYWORDS):
            return True
        return bool(body) and not slide.get('code') and any(
            phrase in body for phrase in ('salva esse', 'compartilha com', 'segue pra', 'manda pra')
        )

    def is_cover(slide: dict) -> bool:
        return not slide.get('body') and not slide.get('code')

    cta_idx = next((i for i in range(1, len(slides) - 1) if is_cta(slides[i])), -1)
    if cta_idx > 0:
        cta = slides.pop(cta_idx)
        slides.append(cta)

    cover_idx = next((i for i in range(1, len(slides)) if is_cover(slides[i])), -1)
    if cover_idx > 0:
        cover = slides.pop(cover_idx)
        slides.insert(0, cover)

    return slides


def extract_json(text: str) -> str:
    start = text.find('{')
    if start < 0:
        return text
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return text[start:]


def fix_json_newlines(raw: str) -> str:
    result = []
    in_string = False
    escaped = False
    for char in raw:
        if escaped:
            result.append(char)
            escaped = False
            continue
        if char == '\\' and in_string:
            result.append(char)
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            result.append(char)
            continue
        if in_string and char == '\n':
            result.extend(['\\', 'n'])
            continue
        if in_string and char == '\r':
            continue
        result.append(char)
    return ''.join(result)


def build_prompt(topic: str, post_type: str, slide_count: int = 7) -> str:
    return f"""Generate an Instagram carousel post about: {topic}

Post type: {post_type}
Number of slides: {slide_count}

Return ONLY valid JSON (no markdown, no code fences) with this structure:
{{
  "title": "catchy title for the post",
  "slides": [
    {{
      "heading": "slide heading (short, impactful)",
      "body": "2-3 lines of content, concise and valuable",
      "code": "optional code snippet if relevant",
      "icon": "optional emoji for visual"
    }}
  ],
  "caption": "Instagram caption",
  "hashtags": ["#relevant", "#hashtags"]
}}

Rules:
- Use Google Cloud products in examples (GKE, Cloud Run, GCS). Never AWS/Azure.
- Slide 1: COVER (title only). Slides 2-{slide_count - 1}: technical content. Slide {slide_count}: CTA.
- Write in Brazilian Portuguese. Keep text short.
- In code fields use literal \\n for newlines inside JSON strings.
- Cover logos are resolved automatically from the topic — do not include cover_svg.
- caption: hook on first line (max 10 words), body 4-6 lines, specific CTA.
- Exactly 5 hashtags in the hashtags array."""


def _parse_ai_json(text: str) -> dict:
    if text.startswith('```'):
        text = text.split('\n', 1)[-1].rsplit('```', 1)[0].strip()
    text = fix_json_newlines(extract_json(text))
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError('Resposta da IA não é JSON válido — tente Regenerar com IA.') from exc


def generate_carousel_with_ai(topic: str, post_type: str = 'cheatsheet', slide_count: int = 7) -> dict:
    """Gera JSON estruturado via Gemini (equivalente ao Claude no instagen)."""
    from config.gemini import generate_text

    prompt = build_prompt(topic, post_type, slide_count)
    text, _model = generate_text(prompt)
    data = _parse_ai_json(text)
    data['slides'] = reorder_slides(data.get('slides') or [])
    data['hashtags'] = (data.get('hashtags') or [])[:5]
    return data


def carousel_from_post(post, post_type: str = 'tip', slide_count: int = 5) -> dict:
    """Deriva carrossel a partir de um post publicado."""
    from config.gemini import generate_text

    topic = post.title_pt or post.title_en
    description = (post.description_pt or post.description_en or '')[:600]
    brief = (
        f'Create an Instagram carousel summarizing this blog post.\n'
        f'Title: {topic}\nDescription: {description}\n'
        f'Post URL placeholder: {{url}}\n'
        f'Type: {post_type}, slides: {slide_count}'
    )
    text, _model = generate_text(build_prompt(brief, post_type, slide_count))
    data = _parse_ai_json(text)
    data['slides'] = reorder_slides(data.get('slides') or [])
    data['hashtags'] = (data.get('hashtags') or [])[:5]
    return data


def slide_context(carousel, slide_index: int) -> dict:
    """Contexto para template Django de um slide (1080×1350)."""
    slides = carousel.slides or []
    total = len(slides)
    idx = max(0, min(slide_index, total - 1)) if total else 0
    slide = slides[idx] if total else {}
    meta = TEMPLATE_META.get(carousel.post_type, TEMPLATE_META['cheatsheet'])

    code = slide.get('code') or ''
    if code:
        code = code.replace('\\n', '\n')

    cover_logos = resolve_cover_logos(
        topic=carousel.topic or '',
        title=carousel.title or '',
        post_type=carousel.post_type or '',
    )

    return {
        'title': carousel.title,
        'slide': slide,
        'slide_num': idx + 1,
        'total_slides': total,
        'is_first': idx == 0,
        'is_last': total > 0 and idx == total - 1,
        'cover_logos': cover_logos,
        'cover_svg': '' if cover_logos else (carousel.cover_svg or ''),
        'badge_label': meta['badge'],
        'bg_gradient': meta['gradient'],
        'code': code,
    }


def caption_text(carousel) -> str:
    tags = ' '.join(carousel.hashtags or [])
    caption = (carousel.caption or '').strip()
    if tags and tags not in caption:
        return f'{caption}\n\n{tags}'.strip()
    return caption
