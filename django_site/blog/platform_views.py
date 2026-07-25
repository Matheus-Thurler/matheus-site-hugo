"""Views for platform features (series, start-here, projects, status, etc.)."""
import hashlib

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from blog.models import Post, PostFeedback, Series
from blog.platform import (
    analytics_dashboard_stats,
    ask_post_question,
    check_homelab_status,
    get_projects_data,
    get_start_here_posts,
    parse_changelog,
)
from blog.views import get_current_language


def series_detail(request, slug):
    lang = get_current_language()
    series = get_object_or_404(Series, slug=slug, is_published=True)
    posts = [
        sp.post for sp in series.series_posts.select_related('post').order_by('order')
        if sp.post.status == 'published'
    ]
    return render(request, 'blog/series_detail.html', {
        'lang': lang,
        'series': series,
        'posts': posts,
        'title': series.get_title(lang),
        'description': series.get_description(lang),
    })


def start_here(request):
    lang = get_current_language()
    posts = get_start_here_posts(lang)
    return render(request, 'blog/start_here.html', {
        'lang': lang,
        'posts': posts,
        'title': 'Comece aqui' if lang == 'pt' else 'Start here',
        'description': (
            'Trilha recomendada para novos leitores'
            if lang == 'pt'
            else 'Recommended path for new readers'
        ),
    })


def projects(request):
    lang = get_current_language()
    repos = get_projects_data()
    return render(request, 'blog/projects.html', {
        'lang': lang,
        'repos': repos,
        'title': 'Projetos' if lang == 'pt' else 'Projects',
        'description': (
            'Repositórios open source'
            if lang == 'pt'
            else 'Open source repositories'
        ),
    })


def status_page(request):
    lang = get_current_language()
    checks = check_homelab_status()
    return render(request, 'blog/status.html', {
        'lang': lang,
        'checks': checks,
        'title': 'Status' if lang == 'pt' else 'Status',
        'description': 'Homelab service status',
    })


def changelog(request):
    lang = get_current_language()
    entries = parse_changelog()
    return render(request, 'blog/changelog.html', {
        'lang': lang,
        'entries': entries,
        'title': 'Changelog',
        'description': 'Site changelog',
    })


def suggest_link(request):
    from curation.forms import LinkSubmissionForm

    lang = get_current_language()
    form = LinkSubmissionForm(request.POST or None)
    success = False
    if request.method == 'POST' and form.is_valid():
        form.save()
        success = True
        form = LinkSubmissionForm()
    return render(request, 'blog/suggest_link.html', {
        'lang': lang,
        'form': form,
        'success': success,
        'title': 'Sugerir link' if lang == 'pt' else 'Suggest a link',
    })


@ratelimit(key='ip', rate='30/m', method='POST', block=True)
@require_POST
def post_feedback(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    helpful_raw = request.POST.get('helpful', '')
    if helpful_raw not in ('1', '0', 'true', 'false'):
        return JsonResponse({'error': 'invalid'}, status=400)
    helpful = helpful_raw in ('1', 'true')
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ip and ',' in ip:
        ip = ip.split(',')[0].strip()
    ua = request.META.get('HTTP_USER_AGENT', '')[:120]
    visitor_hash = hashlib.sha256(f'{ip}|{ua}'.encode()).hexdigest()
    PostFeedback.objects.update_or_create(
        post=post,
        visitor_hash=visitor_hash,
        defaults={'helpful': helpful},
    )
    helpful_count = post.feedback.filter(helpful=True).count()
    total = post.feedback.count()
    return JsonResponse({'ok': True, 'helpful': helpful_count, 'total': total})


@ratelimit(key='ip', rate='10/m', method='POST', block=True)
@require_POST
def post_ask(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    if not getattr(settings, 'GEMINI_API_KEY', ''):
        return JsonResponse({'error': 'not configured'}, status=503)
    question = (request.POST.get('question') or '').strip()
    if not question or len(question) > 500:
        return JsonResponse({'error': 'invalid question'}, status=400)
    lang = get_current_language()
    try:
        answer = ask_post_question(post, question, lang=lang)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)
    return JsonResponse({'answer': answer})


@staff_member_required
def analytics_dashboard(request):
    days = int(request.GET.get('days', 7))
    stats = analytics_dashboard_stats(days=days)
    return render(request, 'admin/analytics_dashboard.html', {
        'stats': stats,
        'title': 'Analytics dashboard',
    })
