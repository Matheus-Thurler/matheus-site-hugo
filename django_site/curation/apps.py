from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CurationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'curation'
    verbose_name = _('Curadoria')
