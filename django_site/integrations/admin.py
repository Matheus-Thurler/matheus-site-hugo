from django.contrib import admin

from .models import IntegrationConfig


@admin.register(IntegrationConfig)
class IntegrationConfigAdmin(admin.ModelAdmin):
    list_display = ('provider', 'is_active', 'last_sync_at', 'last_result')
    list_filter = ('is_active', 'provider')
