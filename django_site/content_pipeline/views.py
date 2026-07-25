"""Internal API for Cloud Scheduler / cron — replaces Pub/Sub triggers."""
import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .scheduler import run_job

logger = logging.getLogger(__name__)


def _check_token(request) -> bool:
    token = request.headers.get('X-Internal-Token', '')
    expected = getattr(settings, 'NEWSLETTER_INTERNAL_TOKEN', '') or getattr(
        settings, 'INTERNAL_API_TOKEN', '',
    )
    return bool(expected) and token == expected


@csrf_exempt
@require_POST
def scheduler_curate(request):
    if not _check_token(request):
        return JsonResponse({'error': 'unauthorized'}, status=401)
    job = run_job('curate')
    return JsonResponse({'ok': job.status == 'success', 'job_id': job.pk, 'log': job.log})


@csrf_exempt
@require_POST
def scheduler_check_content(request):
    if not _check_token(request):
        return JsonResponse({'error': 'unauthorized'}, status=401)
    job = run_job('check_content')
    return JsonResponse({'ok': job.status == 'success', 'job_id': job.pk, 'log': job.log})


@csrf_exempt
@require_POST
def scheduler_sync(request):
    if not _check_token(request):
        return JsonResponse({'error': 'unauthorized'}, status=401)
    from integrations.services import sync_all
    results = sync_all()
    return JsonResponse({'ok': True, 'results': results})


@csrf_exempt
@require_POST
def scheduler_pipeline(request):
    if not _check_token(request):
        return JsonResponse({'error': 'unauthorized'}, status=401)
    from .services import run_pipeline
    job = run_pipeline('full')
    return JsonResponse({'ok': job.status == 'success', 'job_id': job.pk, 'log': job.log})
