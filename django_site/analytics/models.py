import hashlib

from django.db import models
from django.utils.translation import gettext_lazy as _


class PageView(models.Model):
    """Privacy-first pageview — no cookies, path + hashed IP only."""

    path = models.CharField(max_length=500, db_index=True)
    referrer = models.CharField(max_length=500, blank=True)
    visitor_hash = models.CharField(max_length=64, db_index=True)
    post_slug = models.CharField(max_length=120, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Page view')
        verbose_name_plural = _('Page views')

    def __str__(self):
        return f'{self.path} @ {self.created_at:%Y-%m-%d}'

    @staticmethod
    def hash_visitor(ip: str, user_agent: str) -> str:
        raw = f'{ip}|{user_agent[:120]}'
        return hashlib.sha256(raw.encode()).hexdigest()
