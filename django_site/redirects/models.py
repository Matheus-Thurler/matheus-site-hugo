from django.db import models
from django.utils.translation import gettext_lazy as _


class Redirect(models.Model):
    """301/302 redirects — Hugo migration and URL changes."""

    old_path = models.CharField(max_length=500, unique=True, db_index=True)
    new_path = models.CharField(max_length=500)
    is_permanent = models.BooleanField(default=True)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['old_path']
        verbose_name = _('Redirect')
        verbose_name_plural = _('Redirects')

    def __str__(self):
        code = '301' if self.is_permanent else '302'
        return f'{code} {self.old_path} → {self.new_path}'
