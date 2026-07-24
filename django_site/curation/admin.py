from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from config.admin_mixins import DescriptiveAdminMixin
from .models import CuratedItem, FeedSource


@admin.register(FeedSource)
class FeedSourceAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'url', 'is_active', 'max_items')
    list_filter = ('is_active',)
    fieldsets = (
        (None, {
            'fields': ('name', 'url', 'is_active', 'max_items'),
            'description': _('Job de curadoria lê feeds ativos e cria CuratedItems com score IA.'),
        }),
    )


@admin.register(CuratedItem)
class CuratedItemAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'source', 'score', 'status', 'created_at')
    list_filter = ('status', 'source')
    search_fields = ('title', 'url', 'ai_summary')
    actions = ('approve', 'reject')
    readonly_fields = ('created_at',)

    @admin.action(description='Approve selected')
    def approve(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description='Reject selected')
    def reject(self, request, queryset):
        queryset.update(status='rejected')
