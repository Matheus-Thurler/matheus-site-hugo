from django.db import models
from django.utils.translation import gettext_lazy as _


class Page(models.Model):
    """CMS pages — replaces hardcoded about/privacy/terms templates."""

    slug = models.SlugField(max_length=100, unique=True)
    title_en = models.CharField(max_length=200)
    title_pt = models.CharField(max_length=200, blank=True)
    content_en = models.TextField(blank=True)
    content_pt = models.TextField(blank=True)
    meta_description_en = models.CharField(max_length=300, blank=True)
    meta_description_pt = models.CharField(max_length=300, blank=True)
    is_published = models.BooleanField(default=True)
    show_in_footer = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['slug']
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')

    def __str__(self):
        return self.slug

    def get_title(self, lang='en'):
        if lang == 'pt' and self.title_pt:
            return self.title_pt
        return self.title_en

    def get_content(self, lang='en'):
        if lang == 'pt' and self.content_pt:
            return self.content_pt
        return self.content_en
