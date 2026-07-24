from django.db import models
from django.utils.translation import gettext_lazy as _


class IntegrationConfig(models.Model):
    PROVIDERS = [
        ('youtube', 'YouTube'),
        ('github', 'GitHub'),
        ('discord', 'Discord'),
    ]

    provider = models.CharField(max_length=20, choices=PROVIDERS, unique=True)
    is_active = models.BooleanField(default=True)
    config_json = models.JSONField(default=dict, blank=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_result = models.TextField(blank=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = _('Integration')
        verbose_name_plural = _('Integrations')

    def __str__(self):
        return self.get_provider_display()
