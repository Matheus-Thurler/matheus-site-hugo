from django.db import models
from django.utils.translation import gettext_lazy as _


class PipelineJob(models.Model):
    """Orchestration log — curation, sync, newsletter, AI drafts."""

    JOB_TYPES = [
        ('full', _('Full pipeline')),
        ('curation', _('Curation only')),
        ('newsletter', _('Newsletter build')),
        ('sync', _('Integrations sync')),
        ('ai_draft', _('AI draft')),
    ]
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('running', _('Running')),
        ('success', _('Success')),
        ('failed', _('Failed')),
    ]

    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default='full')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    log = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Pipeline job')
        verbose_name_plural = _('Pipeline jobs')

    def __str__(self):
        return f'{self.job_type} — {self.status}'

    def append_log(self, line: str):
        self.log = (self.log + line + '\n') if self.log else line + '\n'
        self.save(update_fields=['log'])
