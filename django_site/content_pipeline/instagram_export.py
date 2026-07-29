"""Export Instagram carousel slides to PNG (1080×1350) via Playwright."""

from __future__ import annotations

import zipfile
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.files import File
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


def media_abspath(relative_path: str) -> Path:
    return Path(settings.MEDIA_ROOT) / relative_path


def carousel_title(carousel) -> str:
    return (carousel.title or carousel.topic or f'Carrossel #{carousel.pk}').strip()


def zip_download_filename(carousel) -> str:
    from django.utils.text import slugify

    base = slugify(carousel_title(carousel))
    return f'{base or f"carrossel-{carousel.pk}"}.zip'


def _slide_tag(carousel, slide_name: str) -> str:
    slide_num = slide_name.removeprefix('slide-').removesuffix('.png')
    return f'carousel:{carousel.pk},slide:{slide_num}'


def build_carousel_zip(carousel, relative_paths: list[str]) -> str:
    """Monta ZIP com todos os PNGs. Retorna path relativo em media/."""
    out_dir = export_dir_for(carousel)
    zip_filename = f'carousel-{carousel.pk}.zip'
    zip_path = out_dir / zip_filename
    rel_zip = str(Path('instagram') / str(carousel.pk) / zip_filename)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for rel in relative_paths:
            abs_path = media_abspath(rel)
            zf.write(abs_path, arcname=abs_path.name)

    return rel_zip


def register_exports_in_media_library(carousel, relative_paths: list[str]) -> int:
    """Copia PNGs para library/ e registra/atualiza MediaAsset. Retorna quantidade."""
    from media_library.models import MediaAsset

    title_base = carousel_title(carousel)
    created_or_updated = 0

    for rel in relative_paths:
        slide_name = rel.rsplit('/', 1)[-1]
        tag_key = _slide_tag(carousel, slide_name)
        asset_title = f'{title_base} — {slide_name}'
        src = media_abspath(rel)

        asset = MediaAsset.objects.filter(tags__contains=tag_key).first()
        if asset is None:
            asset = MediaAsset(
                title=asset_title,
                tags=f'instagram,{tag_key}',
                caption=title_base,
            )

        with src.open('rb') as handle:
            asset.file.save(slide_name, File(handle), save=False)
        asset.title = asset_title
        asset.caption = title_base
        asset.tags = f'instagram,{tag_key}'
        asset.save()
        created_or_updated += 1

    return created_or_updated


def register_zip_in_media_library(carousel, zip_rel_path: str) -> None:
    """Registra o ZIP do carrossel na Media Library."""
    from media_library.models import MediaAsset

    title_base = carousel_title(carousel)
    zip_name = zip_rel_path.rsplit('/', 1)[-1]
    tag_key = f'carousel:{carousel.pk},zip'

    asset = MediaAsset.objects.filter(tags__contains=tag_key).first()
    if asset is None:
        asset = MediaAsset(
            title=f'{title_base} — ZIP',
            tags=f'instagram,{tag_key}',
            caption=f'ZIP com {carousel.slide_count} slides',
        )

    src = media_abspath(zip_rel_path)
    with src.open('rb') as handle:
        asset.file.save(zip_name, File(handle), save=False)
    asset.title = f'{title_base} — ZIP'
    asset.caption = f'ZIP com {carousel.slide_count} slides'
    asset.tags = f'instagram,{tag_key}'
    asset.save()


def export_carousel_pngs(carousel, *, force: bool = False) -> list[str]:
    """Renderiza cada slide, salva PNG, monta ZIP e registra na Media Library."""
    if not carousel.slide_count:
        raise InstagramExportError('Carrossel sem slides — gere o preview antes.')

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise InstagramExportError(
            'Playwright não instalado no servidor. '
            'Rebuild da imagem Docker com playwright no pyproject.toml.'
        ) from exc

    out_dir = export_dir_for(carousel)
    out_dir.mkdir(parents=True, exist_ok=True)

    relative_paths: list[str] = []

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage'],
            )
        except Exception as exc:
            raise InstagramExportError(
                'Chromium do Playwright não encontrado. '
                'Local: uv run playwright install chromium. '
                'Docker: rebuild da imagem após atualizar o Dockerfile.'
            ) from exc
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

    zip_rel_path = build_carousel_zip(carousel, relative_paths)
    register_exports_in_media_library(carousel, relative_paths)
    register_zip_in_media_library(carousel, zip_rel_path)

    carousel.export_paths = relative_paths
    carousel.export_zip_path = zip_rel_path
    carousel.exported_at = timezone.now()
    if carousel.status == 'draft':
        carousel.status = 'ready'
    carousel.save(update_fields=['export_paths', 'export_zip_path', 'exported_at', 'status'])
    return relative_paths
