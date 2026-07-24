from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils import translation

from blog.markdown_utils import render_markdown
from .models import Page


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_published=True)
    lang = translation.get_language() or 'en'
    content_md = page.get_content(lang)
    return render(request, 'pages/page_detail.html', {
        'page': page,
        'page_title': page.get_title(lang),
        'page_content': render_markdown(content_md) if content_md else '',
        'meta_description': (
            page.meta_description_pt if lang == 'pt' and page.meta_description_pt
            else page.meta_description_en
        ),
    })


def get_published_page(slug):
    try:
        return Page.objects.get(slug=slug, is_published=True)
    except Page.DoesNotExist:
        raise Http404
