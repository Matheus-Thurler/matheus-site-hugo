"""Discord Bot API client — same channels as content-automation."""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

DISCORD_API = 'https://discord.com/api/v10'


def _headers():
    token = getattr(settings, 'DISCORD_BOT_TOKEN', '')
    if not token:
        raise ValueError('DISCORD_BOT_TOKEN is not configured')
    return {
        'Authorization': f'Bot {token}',
        'Content-Type': 'application/json',
    }


def send_message(channel_id, *, content=None, embeds=None, components=None):
    payload = {}
    if content:
        payload['content'] = content[:2000]
    if embeds:
        payload['embeds'] = embeds
    if components is not None:
        payload['components'] = components
    resp = requests.post(
        f'{DISCORD_API}/channels/{channel_id}/messages',
        headers=_headers(),
        json=payload,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def update_message(channel_id, message_id, *, content=None, embeds=None, components=None):
    payload = {}
    if content is not None:
        payload['content'] = content[:2000] if content else content
    if embeds is not None:
        payload['embeds'] = embeds
    if components is not None:
        payload['components'] = components
    resp = requests.patch(
        f'{DISCORD_API}/channels/{channel_id}/messages/{message_id}',
        headers=_headers(),
        json=payload,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def post_draft_for_review(campaign):
    """Post newsletter draft with Approve/Reject buttons (custom_id: approve_campaign_{pk})."""
    from django.conf import settings

    channel_id = settings.DISCORD_DRAFTS_CHANNEL_ID
    body = campaign.body_markdown or campaign.body_html_pt or campaign.body_html_en or ''
    embed = {
        'title': '📝 Draft pronto para revisão',
        'description': body[:4096],
        'color': 0xEBCB8B,
        'footer': {'text': f'Campaign #{campaign.pk} — {campaign.subject_pt or campaign.subject_en}'},
    }
    components = [{
        'type': 1,
        'components': [
            {
                'type': 2,
                'style': 3,
                'label': 'Aprovar',
                'custom_id': f'approve_campaign_{campaign.pk}',
            },
            {
                'type': 2,
                'style': 4,
                'label': 'Rejeitar',
                'custom_id': f'reject_campaign_{campaign.pk}',
            },
        ],
    }]
    msg = send_message(channel_id, embeds=[embed], components=components)
    return msg


def post_to_newsletter_channel(content, title=''):
    from django.conf import settings

    embed = {
        'title': f'📬 {title}' if title else '📬 Nova Newsletter',
        'description': content[:4096],
        'color': 0x88C0D0,
    }
    return send_message(settings.DISCORD_NEWSLETTER_CHANNEL_ID, embeds=[embed])


def post_new_content_items(items):
    """Post new blog/video items to newsletter channel."""
    from django.conf import settings

    channel_id = settings.DISCORD_NEWSLETTER_CHANNEL_ID
    for item in items:
        emoji = '🎬' if item.get('type') == 'video' else '📝'
        embed = {
            'title': f'{emoji} {item["title"]}',
            'url': item['url'],
            'color': 0xA3BE8C,
        }
        send_message(channel_id, embeds=[embed])
