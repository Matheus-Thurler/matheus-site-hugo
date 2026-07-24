"""Handle Discord interaction webhook (button clicks)."""
import json
import logging

from django.conf import settings
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

logger = logging.getLogger(__name__)


def verify_signature(raw_body: bytes, signature: str | None, timestamp: str | None) -> bool:
    public_key = getattr(settings, 'DISCORD_PUBLIC_KEY', '')
    if not public_key or not signature or not timestamp:
        return False
    try:
        verify_key = VerifyKey(bytes.fromhex(public_key))
        verify_key.verify(f'{timestamp}{raw_body.decode()}'.encode(), bytes.fromhex(signature))
        return True
    except (BadSignatureError, ValueError, Exception) as exc:
        logger.warning('Discord signature verification failed: %s', exc)
        return False


def handle_interaction(body: dict) -> dict:
    interaction_type = body.get('type')

    # PING — Discord endpoint verification
    if interaction_type == 1:
        return {'type': 1}

    # MESSAGE_COMPONENT — button click
    if interaction_type == 3:
        custom_id = body['data']['custom_id']
        channel_id = body['channel_id']
        message_id = body['message']['id']

        if custom_id.startswith('approve_campaign_'):
            pk = int(custom_id.replace('approve_campaign_', ''))
            return _handle_approve_campaign(pk, channel_id, message_id)

        if custom_id.startswith('reject_campaign_'):
            pk = int(custom_id.replace('reject_campaign_', ''))
            return _handle_reject_campaign(pk, channel_id, message_id)

    return {'type': 4, 'data': {'content': 'Interação desconhecida', 'flags': 64}}


def _handle_approve_campaign(pk: int, channel_id: str, message_id: str) -> dict:
    from campaigns.services import approve_and_send_campaign
    from discord_bot.client import update_message

    try:
        title = approve_and_send_campaign(pk)
    except Exception as exc:
        logger.exception('Approve campaign %s failed', pk)
        return {'type': 4, 'data': {'content': f'❌ Erro ao aprovar: {exc}', 'flags': 64}}

    update_message(channel_id, message_id, components=[])
    return {
        'type': 4,
        'data': {
            'content': f'✅ Draft aprovado! Newsletter enviada: **{title}**',
            'flags': 64,
        },
    }


def _handle_reject_campaign(pk: int, channel_id: str, message_id: str) -> dict:
    from campaigns.models import NewsletterCampaign
    from discord_bot.client import update_message

    NewsletterCampaign.objects.filter(pk=pk).update(status='rejected')
    update_message(channel_id, message_id, components=[])
    return {
        'type': 4,
        'data': {'content': f'❌ Draft #{pk} rejeitado.', 'flags': 64},
    }
