from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ContentPipelineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'content_pipeline'
    verbose_name = _('Pipeline automático')
