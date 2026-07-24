import json

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from .models import PageView


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


@csrf_exempt
@require_POST
@ratelimit(key='ip', rate='120/m', method='POST', block=True)
def track(request):
    if not getattr(settings, 'ANALYTICS_SELF_HOSTED', True):
        return JsonResponse({'ok': False}, status=403)
    try:
        payload = json.loads(request.body.decode() or '{}')
    except json.JSONDecodeError:
        payload = request.POST

    path = (payload.get('path') or request.META.get('HTTP_REFERER') or '/')[:500]
    referrer = (payload.get('referrer') or '')[:500]
    post_slug = (payload.get('post_slug') or '')[:120]
    ua = request.META.get('HTTP_USER_AGENT', '')
    ip = _client_ip(request)

    PageView.objects.create(
        path=path,
        referrer=referrer,
        visitor_hash=PageView.hash_visitor(ip, ua),
        post_slug=post_slug,
    )
    return JsonResponse({'ok': True})
