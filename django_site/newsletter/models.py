import base64

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Subscriber(models.Model):
    """Newsletter subscriber — replaces GCS subscribers.json from content-automation."""

    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('pt', _('Portuguese')),
    ]

    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    is_active = models.BooleanField(default=True, db_index=True)
    subscribed_at = models.DateTimeField(default=timezone.now)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = _('Subscriber')
        verbose_name_plural = _('Subscribers')

    def __str__(self):
        return f'{self.name} <{self.email}>'

    @property
    def unsubscribe_token(self):
        """Base64 token compatible with content-automation Cloud Functions."""
        return base64.urlsafe_b64encode(self.email.encode()).decode()

    def to_export_dict(self):
        return {
            'email': self.email,
            'name': self.name,
            'subscribed_at': self.subscribed_at.isoformat(),
            'language': self.language,
        }
