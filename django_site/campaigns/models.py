from django.db import models
from django.utils.translation import gettext_lazy as _


class NewsletterCampaign(models.Model):
    STATUS_CHOICES = [
        ('pending_review', _('Pending review')),
        ('draft', _('Draft')),
        ('scheduled', _('Scheduled')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('sent', _('Sent')),
        ('failed', _('Failed')),
    ]

    subject_en = models.CharField(max_length=200)
    subject_pt = models.CharField(max_length=200, blank=True)
    body_markdown = models.TextField(blank=True, help_text='Weekly curation draft (PT-BR markdown)')
    body_html_en = models.TextField(blank=True)
    body_html_pt = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='draft')
    discord_message_id = models.CharField(max_length=32, blank=True)
    discord_channel_id = models.CharField(max_length=32, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    recipient_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Newsletter campaign')
        verbose_name_plural = _('Newsletter campaigns')

    def __str__(self):
        return f'{self.subject_en} ({self.status})'
