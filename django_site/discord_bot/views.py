import json
import logging

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .interactions import handle_interaction, verify_signature

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def discord_interactions(request):
    """Discord Interactions endpoint — replace content-automation Cloud Function."""
    raw = request.body
    if not verify_signature(
        raw,
        request.headers.get('X-Signature-Ed25519'),
        request.headers.get('X-Signature-Timestamp'),
    ):
        return HttpResponse('invalid signature', status=401)

    body = json.loads(raw.decode())
    result = handle_interaction(body)
    return JsonResponse(result)
