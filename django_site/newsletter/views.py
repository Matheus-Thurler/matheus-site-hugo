import base64
import csv
import json
import re

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit

from .models import Subscriber
from .services import send_welcome_email

EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


def _cors_headers():
    origin = getattr(settings, 'NEWSLETTER_ALLOWED_ORIGIN', 'https://matheusthurler.com.br')
    return {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, X-CSRFToken',
        'Access-Control-Max-Age': '3600',
    }


def _json_response(body, status=200):
    response = JsonResponse(body, status=status)
    for key, value in _cors_headers().items():
        response[key] = value
    return response


def _parse_subscribe_request(request):
    content_type = request.content_type or ''
    if 'application/json' in content_type:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}
    else:
        data = {
            'email': request.POST.get('email', ''),
            'name': request.POST.get('name', ''),
        }
    return data.get('email', '').strip(), data.get('name', '').strip()


def _current_language(request):
    lang = getattr(request, 'LANGUAGE_CODE', 'en') or 'en'
    return lang if lang in ('en', 'pt') else 'en'


@ratelimit(key='ip', rate='10/m', method='POST', block=True)
@csrf_exempt
@require_http_methods(['POST', 'OPTIONS'])
def subscribe(request):
    """
    Subscribe endpoint — API-compatible with content-automation Cloud Function.
    POST JSON: {"email": "...", "name": "..."}
    """
    if request.method == 'OPTIONS':
        response = HttpResponse(status=204)
        for key, value in _cors_headers().items():
            response[key] = value
        return response

    if getattr(request, 'limited', False):
        return _json_response({'error': 'rate limit exceeded'}, 429)

    email, name = _parse_subscribe_request(request)
    language = _current_language(request)

    if not email:
        return _json_response({'error': 'email is required'}, 400)

    if not EMAIL_RE.match(email):
        return _json_response({'error': 'invalid email format'}, 400)

    if not name:
        return _json_response({'error': 'name is required'}, 400)

    existing = Subscriber.objects.filter(email__iexact=email).first()
    if existing:
        if existing.is_active:
            return _json_response({'message': 'already subscribed'}, 200)
        existing.is_active = True
        existing.name = name
        existing.language = language
        existing.unsubscribed_at = None
        existing.subscribed_at = timezone.now()
        existing.save(update_fields=['is_active', 'name', 'language', 'unsubscribed_at', 'subscribed_at'])
        send_welcome_email(email, name, language)
        return _json_response({'message': 'subscribed'}, 201)

    Subscriber.objects.create(email=email, name=name, language=language)
    send_welcome_email(email, name, language)

    return _json_response({'message': 'subscribed'}, 201)


@require_http_methods(['GET', 'OPTIONS'])
def unsubscribe(request):
    """Unsubscribe via base64 token — compatible with content-automation emails."""
    if request.method == 'OPTIONS':
        response = HttpResponse(status=204)
        response['Access-Control-Allow-Origin'] = '*'
        return response

    token = request.GET.get('token')
    if token:
        try:
            email = base64.urlsafe_b64decode(token).decode('utf-8').strip().lower()
            Subscriber.objects.filter(email__iexact=email, is_active=True).update(
                is_active=False,
                unsubscribed_at=timezone.now(),
            )
        except Exception:
            pass

    return HttpResponse(_unsubscribe_html(), content_type='text/html; charset=utf-8')


def _unsubscribe_html():
    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Inscrição cancelada</title>
<style>
body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#2E3440;color:#ECEFF4;font-family:system-ui,sans-serif}
.card{text-align:center;padding:2rem}
h1{color:#88C0D0;font-size:1.5rem;margin-bottom:.5rem}
p{margin:.5rem 0;opacity:.85}
a{color:#88C0D0;text-decoration:none;margin-top:1.5rem;display:inline-block}
a:hover{text-decoration:underline}
</style>
</head>
<body>
<div class="card">
<h1>Inscrição cancelada com sucesso</h1>
<p>Você não receberá mais emails da newsletter.</p>
<a href="https://matheusthurler.com.br">← Voltar para matheusthurler.com.br</a>
</div>
</body>
</html>"""


def _check_internal_token(request):
    token = request.headers.get('X-Internal-Token', '')
    expected = getattr(settings, 'NEWSLETTER_INTERNAL_TOKEN', '')
    return expected and token == expected


@require_http_methods(['GET'])
def subscribers_api(request):
    """
    Export active subscribers as JSON — drop-in replacement for GCS subscribers.json.
    Used by content-automation newsletter function during migration.
    Requires X-Internal-Token header.
    """
    if not _check_internal_token(request):
        return JsonResponse({'error': 'unauthorized'}, status=401)

    subscribers = [
        sub.to_export_dict()
        for sub in Subscriber.objects.filter(is_active=True).order_by('subscribed_at')
    ]
    return JsonResponse({'subscribers': subscribers})


@require_http_methods(['GET'])
def export_csv(request):
    """Admin-only CSV export via token or staff session."""
    if not request.user.is_staff and not _check_internal_token(request):
        return JsonResponse({'error': 'unauthorized'}, status=401)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'
    writer = csv.writer(response)
    writer.writerow(['email', 'name', 'language', 'subscribed_at', 'is_active'])
    for sub in Subscriber.objects.all().order_by('-subscribed_at'):
        writer.writerow([
            sub.email,
            sub.name,
            sub.language,
            sub.subscribed_at.isoformat(),
            sub.is_active,
        ])
    return response


def lead_magnet(request, slug):
    """Lead magnet landing page with newsletter signup gate."""
    from django.shortcuts import get_object_or_404, render

    from .models import LeadMagnet

    magnet = get_object_or_404(LeadMagnet, slug=slug, is_active=True)
    lang = _current_language(request)
    if request.GET.get('download') and request.GET.get('token') == 'subscribed':
        return render(request, 'newsletter/lead_magnet_success.html', {
            'magnet': magnet,
            'lang': lang,
            'download_url': magnet.get_download_url(),
        })
    return render(request, 'newsletter/lead_magnet.html', {
        'magnet': magnet,
        'lang': lang,
        'newsletter_url': '/newsletter/subscribe/',
    })
