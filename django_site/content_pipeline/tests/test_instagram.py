import pytest
from django.utils import timezone

from content_pipeline.instagram import find_duplicate_carousel, normalize_topic_key, reorder_slides
from content_pipeline.instagram_export import (
    build_carousel_zip,
    export_dir_for,
    register_exports_in_media_library,
    register_zip_in_media_library,
    zip_download_filename,
)
from content_pipeline.models import InstagramCarousel
from media_library.models import MediaAsset


def test_reorder_slides_puts_cta_last():
    slides = [
        {'heading': 'Cover', 'body': '', 'code': ''},
        {'heading': 'Segue pra mais', 'body': 'Segue @maththurler.devops', 'code': ''},
        {'heading': 'kubectl get', 'body': 'Lista pods', 'code': 'kubectl get pods'},
    ]
    ordered = reorder_slides(slides)
    assert ordered[0]['heading'] == 'Cover'
    assert ordered[-1]['heading'] == 'Segue pra mais'
    assert ordered[1]['heading'] == 'kubectl get'


def test_normalize_topic_key_comparison_is_order_invariant():
    a = normalize_topic_key(title='Kustomize vs ArgoCD: Qual a diferença?')
    b = normalize_topic_key(title='ArgoCD vs Kustomize')
    assert a == b == 'argocd vs kustomize'


def test_normalize_topic_key_strips_noise():
    key = normalize_topic_key(topic='Diferenças entre nginx e traefik no kubernetes')
    assert key == 'nginx vs traefik'


@pytest.mark.django_db
def test_find_duplicate_carousel():
    first = InstagramCarousel.objects.create(
        title='Kustomize vs ArgoCD',
        topic='kustomize vs argocd',
        slides=[{'heading': 'x'}],
    )
    dup = find_duplicate_carousel(title='ArgoCD vs Kustomize', topic='')
    assert dup == first

    other = InstagramCarousel.objects.create(title='Helm tips', topic='helm tips', slides=[{'heading': 'y'}])
    assert find_duplicate_carousel(title='Helm tips', exclude_pk=other.pk) is None


@pytest.mark.django_db
def test_carousel_save_sets_topic_key():
    carousel = InstagramCarousel(title='Docker vs Kubernetes', slides=[{'heading': 'a'}])
    carousel.save()
    assert carousel.topic_key == 'docker vs kubernetes'


@pytest.mark.django_db
def test_export_paths_persisted():
    carousel = InstagramCarousel.objects.create(
        title='Test export',
        topic='test export',
        slides=[{'heading': 'Cover', 'body': ''}, {'heading': 'CTA', 'body': 'segue'}],
    )
    carousel.export_paths = ['instagram/1/slide-01.png']
    carousel.exported_at = timezone.now()
    carousel.status = 'ready'
    carousel.save()
    carousel.refresh_from_db()
    assert carousel.is_exported
    assert carousel.export_paths[0].endswith('.png')


@pytest.mark.django_db
def test_zip_download_filename():
    carousel = InstagramCarousel(title='Kubectl Tips!', pk=7)
    assert zip_download_filename(carousel) == 'kubectl-tips.zip'


@pytest.mark.django_db
def test_export_zip_view_downloads_file(client, django_user_model, tmp_path, settings, monkeypatch):
    settings.MEDIA_ROOT = tmp_path
    user = django_user_model.objects.create_superuser('admin', 'a@b.com', 'pass')
    client.force_login(user)

    carousel = InstagramCarousel.objects.create(
        title='Download test',
        topic='download test',
        slides=[{'heading': 'Cover', 'body': ''}, {'heading': 'CTA', 'body': ''}],
    )
    out_dir = export_dir_for(carousel)
    out_dir.mkdir(parents=True)
    rel_paths = []
    for name in ('slide-01.png', 'slide-02.png'):
        path = out_dir / name
        path.write_bytes(b'png')
        rel_paths.append(str(path.relative_to(tmp_path)))
    zip_rel = build_carousel_zip(carousel, rel_paths)
    carousel.export_paths = rel_paths
    carousel.export_zip_path = zip_rel
    carousel.save()

    url = f'/admin/content_pipeline/instagramcarousel/{carousel.pk}/export-zip/'
    response = client.post(url)

    assert response.status_code == 200
    assert response['Content-Disposition'].startswith('attachment')
    assert 'download-test.zip' in response['Content-Disposition']
    body = b''.join(response.streaming_content)
    assert body[:2] == b'PK'


@pytest.mark.django_db
def test_build_carousel_zip(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    carousel = InstagramCarousel.objects.create(
        title='Zip test',
        topic='zip test',
        slides=[{'heading': 'Cover', 'body': ''}, {'heading': 'CTA', 'body': 'segue'}],
    )
    out_dir = export_dir_for(carousel)
    out_dir.mkdir(parents=True)
    rel_paths = []
    for name in ('slide-01.png', 'slide-02.png'):
        path = out_dir / name
        path.write_bytes(b'fake-png')
        rel_paths.append(str(path.relative_to(tmp_path)))

    zip_rel = build_carousel_zip(carousel, rel_paths)
    zip_path = tmp_path / zip_rel

    assert zip_path.is_file()
    assert zip_rel.endswith(f'carousel-{carousel.pk}.zip')


@pytest.mark.django_db
def test_register_exports_in_media_library(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    carousel = InstagramCarousel.objects.create(
        title='Media lib test',
        topic='media lib test',
        slides=[{'heading': 'Cover', 'body': ''}],
    )
    out_dir = export_dir_for(carousel)
    out_dir.mkdir(parents=True)
    slide_path = out_dir / 'slide-01.png'
    slide_path.write_bytes(b'fake-png')
    rel_path = str(slide_path.relative_to(tmp_path))

    count = register_exports_in_media_library(carousel, [rel_path])
    assert count == 1
    asset = MediaAsset.objects.get(tags__contains=f'carousel:{carousel.pk}')
    assert asset.title.endswith('slide-01.png')
    assert 'instagram' in asset.tags
    assert asset.file.name.startswith('library/')


@pytest.mark.django_db
def test_register_zip_in_media_library(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    carousel = InstagramCarousel.objects.create(
        title='Zip library',
        topic='zip library',
        slides=[{'heading': 'Cover', 'body': ''}, {'heading': 'CTA', 'body': ''}],
    )
    out_dir = export_dir_for(carousel)
    out_dir.mkdir(parents=True)
    zip_rel = f'instagram/{carousel.pk}/carousel-{carousel.pk}.zip'
    zip_path = tmp_path / zip_rel
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    zip_path.write_bytes(b'fake-zip')

    register_zip_in_media_library(carousel, zip_rel)
    asset = MediaAsset.objects.get(tags__contains=f'carousel:{carousel.pk},zip')
    assert asset.title.endswith('ZIP')
    assert asset.file.name.startswith('library/')
