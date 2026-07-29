"""Invalidate page cache when blog content changes."""

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from blog.models import Category, Post, Tag


@receiver(post_save, sender=Post)
@receiver(post_delete, sender=Post)
@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
@receiver(post_save, sender=Tag)
@receiver(post_delete, sender=Tag)
def invalidate_page_cache(sender, **kwargs):
    cache.clear()
