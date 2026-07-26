"""Export Instagram carousel slides to PNG (1080×1350) via Playwright."""

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from django.utils import timezone

from content_pipeline.instagram import slide_context

SLIDE_WIDTH = 1080
SLIDE_HEIGHT = 1350


class InstagramExportError(Exception):
    pass


def _static_uri(relative_path: str) -> str:
    found = finders.find(relative_path)
    if not found:
        raise InstagramExportError(f'Arquivo estático não encontrado: {relative_path}')
    return Path(found).as_uri()


def _inline_css() -> str:
    css_path = finders.find('css/instagram-slide.css')
    if not css_path:
        raise InstagramExportError('css/instagram-slide.css não encontrado')
    return Path(css_path).read_text(encoding='utf-8')


def build_slide_export_html(carousel, slide_index: int) -> str:
    ctx = slide_context(carousel, slide_index)
    ctx['inline_css'] = _inline_css()
    ctx['avatar_uri'] = _static_uri('images/avatar.png')
    for logo in ctx.get('cover_logos') or []:
        logo['uri'] = _static_uri(str(logo['file']))
    return render_to_string('social/instagram/slide_export.html', ctx)


def export_dir_for(carousel) -> Path:
    return Path(settings.MEDIA_ROOT) / 'instagram' / str(carousel.pk)


def export_carousel_pngs(carousel, *, force: bool = False) -> list[str]:
    """Renderiza cada slide e salva PNG em media/instagram/<id>/. Retorna paths relativos."""
    if not carousel.slide_count:
        raise InstagramExportError('Carrossel sem slides — gere o preview antes.')

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise InstagramExportError(
            'Playwright não instalado. Rode: uv sync --group dev && uv run playwright install chromium'
        ) from exc

    out_dir = export_dir_for(carousel)
    out_dir.mkdir(parents=True, exist_ok=True)

    relative_paths: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': SLIDE_WIDTH, 'height': SLIDE_HEIGHT})
        try:
            for index in range(carousel.slide_count):
                filename = f'slide-{index + 1:02d}.png'
                out_path = out_dir / filename
                rel_path = str(Path('instagram') / str(carousel.pk) / filename)

                if out_path.exists() and not force:
                    relative_paths.append(rel_path)
                    continue

                html = build_slide_export_html(carousel, index)
                page.set_content(html, wait_until='load')
                page.locator('.instagram-slide-canvas').screenshot(path=str(out_path), type='png')
                relative_paths.append(rel_path)
        finally:
            browser.close()

    carousel.export_paths = relative_paths
    carousel.exported_at = timezone.now()
    if carousel.status == 'draft':
        carousel.status = 'ready'
    carousel.save(update_fields=['export_paths', 'exported_at', 'status'])
    return relative_paths


def media_abspath(relative_path: str) -> Path:
    return Path(settings.MEDIA_ROOT) / relative_path
