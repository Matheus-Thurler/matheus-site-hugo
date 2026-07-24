from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DiscordBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'discord_bot'
    verbose_name = _('Discord (bot)')
