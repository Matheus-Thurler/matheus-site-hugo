from django.db import models
from django.utils.translation import gettext_lazy as _


class FeedSource(models.Model):
    name = models.CharField(max_length=120)
    url = models.URLField(max_length=500)
    is_active = models.BooleanField(default=True)
    max_items = models.PositiveSmallIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Feed source')
        verbose_name_plural = _('Feed sources')

    def __str__(self):
        return self.name


class CuratedItem(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('published', _('Published')),
    ]

    source = models.ForeignKey(FeedSource, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=500)
    url = models.URLField(max_length=1000, unique=True)
    raw_summary = models.TextField(blank=True)
    ai_summary = models.TextField(blank=True)
    score = models.PositiveSmallIntegerField(default=0)
    tags = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    post = models.ForeignKey(
        'blog.Post', null=True, blank=True, on_delete=models.SET_NULL, related_name='curated_items',
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', '-created_at']
        verbose_name = _('Curated item')
        verbose_name_plural = _('Curated items')

    def __str__(self):
        return self.title[:80]


class LinkSubmission(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
    ]

    title = models.CharField(max_length=500)
    url = models.URLField(max_length=1000)
    submitter_email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    curated_item = models.ForeignKey(
        CuratedItem,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='submissions',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Link submission')
        verbose_name_plural = _('Link submissions')

    def __str__(self):
        return self.title[:80]
