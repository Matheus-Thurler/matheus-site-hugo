from django.contrib import admin

from .models import CuratedItem, FeedSource


@admin.register(FeedSource)
class FeedSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'is_active', 'max_items')
    list_filter = ('is_active',)


@admin.register(CuratedItem)
class CuratedItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'score', 'status', 'created_at')
    list_filter = ('status', 'source')
    search_fields = ('title', 'url', 'ai_summary')
    actions = ('approve', 'reject')

    @admin.action(description='Approve selected')
    def approve(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description='Reject selected')
    def reject(self, request, queryset):
        queryset.update(status='rejected')
