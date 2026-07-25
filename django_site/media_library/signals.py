"""Generate WebP variants for uploaded media assets."""
import logging
from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image

from .models import MediaAsset

logger = logging.getLogger(__name__)


@receiver(post_save, sender=MediaAsset)
def generate_webp_variant(sender, instance, created, **kwargs):
    if not created or not instance.file:
        return
    name = instance.file.name.lower()
    if not name.endswith(('.png', '.jpg', '.jpeg')):
        return
    webp_name = str(Path(instance.file.name).with_suffix('.webp'))
    if default_storage.exists(webp_name):
        return
    try:
        with instance.file.open('rb') as handle:
            image = Image.open(handle)
            image.load()
        buffer = BytesIO()
        image.save(buffer, format='WEBP', quality=85)
        default_storage.save(webp_name, ContentFile(buffer.getvalue()))
        logger.info('Generated WebP variant: %s', webp_name)
    except Exception as exc:
        logger.warning('WebP generation skipped for %s: %s', instance.pk, exc)
