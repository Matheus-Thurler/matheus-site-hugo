"""Send newsletter campaigns to active subscribers."""
import logging

import markdown as md
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


def _markdown_to_html(text: str) -> str:
    if not text:
        return ''
    return md.markdown(text, extensions=['extra', 'nl2br'])


def send_campaign(campaign):
    from newsletter.models import Subscriber

    subscribers = Subscriber.objects.filter(is_active=True)
    sent = 0
    for sub in subscribers:
        lang = sub.language or 'en'
        subject = campaign.subject_pt if lang == 'pt' and campaign.subject_pt else campaign.subject_en
        html = campaign.body_html_pt if lang == 'pt' and campaign.body_html_pt else campaign.body_html_en
        if not html and campaign.body_markdown:
            html = _wrap_email_html(campaign.body_markdown)
        if not subject or not html:
            continue
        msg = EmailMultiAlternatives(
            subject=subject,
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[sub.email],
        )
        msg.attach_alternative(html, 'text/html')
        try:
            msg.send(fail_silently=False)
            sent += 1
        except Exception as exc:
            logger.exception('Failed to send campaign to %s: %s', sub.email, exc)

    campaign.status = 'sent'
    campaign.sent_at = timezone.now()
    campaign.recipient_count = sent
    campaign.save(update_fields=['status', 'sent_at', 'recipient_count'])
    return sent


def _wrap_email_html(body_markdown: str) -> str:
    inner = _markdown_to_html(body_markdown)
    return f'''<!DOCTYPE html><html><body style="font-family:system-ui,sans-serif;background:#2E3440;color:#ECEFF4;padding:24px">
<div style="max-width:600px;margin:0 auto">{inner}</div></body></html>'''


def approve_and_send_campaign(campaign_id: int) -> str:
    """Approve draft, send emails, post to Discord newsletter channel."""
    from .models import NewsletterCampaign
    from discord_bot.client import post_to_newsletter_channel

    campaign = NewsletterCampaign.objects.get(pk=campaign_id)
    if campaign.status in ('sent', 'rejected'):
        raise ValueError(f'Campaign #{campaign_id} already {campaign.status}')

    if campaign.body_markdown and not campaign.body_html_pt:
        campaign.body_html_pt = _wrap_email_html(campaign.body_markdown)
        campaign.body_html_en = campaign.body_html_pt
        campaign.save(update_fields=['body_html_pt', 'body_html_en'])

    campaign.status = 'approved'
    campaign.save(update_fields=['status'])

    title = campaign.subject_pt or campaign.subject_en
    post_to_newsletter_channel(campaign.body_markdown or '', title=title)
    send_campaign(campaign)
    return title


def build_weekly_campaign():
    """Build draft campaign from recent posts + approved curation items."""
    from blog.models import Post
    from curation.models import CuratedItem

    posts = Post.objects.published().order_by('-published_at')[:5]
    curated = CuratedItem.objects.filter(status='approved').order_by('-score')[:5]

    context = {'posts': posts, 'curated': curated, 'site_url': 'https://matheusthurler.com.br'}
    html_en = render_to_string('campaigns/email_weekly_en.html', context)
    html_pt = render_to_string('campaigns/email_weekly_pt.html', context)

    from .models import NewsletterCampaign
    return NewsletterCampaign.objects.create(
        subject_en='Weekly DevOps digest',
        subject_pt='Resumo semanal DevOps',
        body_html_en=html_en,
        body_html_pt=html_pt,
        status='draft',
    )
