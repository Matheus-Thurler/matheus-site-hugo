from django.contrib import admin

from config.admin_mixins import DescriptiveAdminMixin
from .models import IntegrationConfig


@admin.register(IntegrationConfig)
class IntegrationConfigAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('provider', 'is_active', 'last_sync_at', 'last_result')
    list_filter = ('is_active', 'provider')
    readonly_fields = ('last_sync_at', 'last_result')
