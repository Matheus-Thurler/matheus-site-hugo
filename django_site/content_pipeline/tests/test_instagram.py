import pytest
from django.utils import timezone

from content_pipeline.instagram import find_duplicate_carousel, normalize_topic_key, reorder_slides
from content_pipeline.models import InstagramCarousel


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
