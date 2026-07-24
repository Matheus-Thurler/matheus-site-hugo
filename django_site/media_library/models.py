from django.db import models
from django.utils.translation import gettext_lazy as _


class MediaAsset(models.Model):
    """Central media library — covers, diagrams, gallery images."""

    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='library/%Y/%m/')
    alt_text = models.CharField(max_length=300, blank=True)
    caption = models.CharField(max_length=500, blank=True)
    tags = models.CharField(max_length=300, blank=True, help_text='Comma-separated tags')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = _('Media asset')
        verbose_name_plural = _('Media library')

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]
