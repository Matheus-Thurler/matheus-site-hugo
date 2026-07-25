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
    list_display = ('title', 'source', 'score', 'status', 'post', 'created_at')
    list_filter = ('status', 'source')
    search_fields = ('title', 'url', 'ai_summary')
    actions = ('approve', 'reject', 'create_draft_post')
    readonly_fields = ('created_at',)

    @admin.action(description='Approve selected')
    def approve(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description='Reject selected')
    def reject(self, request, queryset):
        queryset.update(status='rejected')

    @admin.action(description='Create draft post from selected')
    def create_draft_post(self, request, queryset):
        from .services import create_post_draft

        created = skipped = 0
        for item in queryset:
            if item.status == 'rejected':
                skipped += 1
                continue
            if item.post_id:
                skipped += 1
                continue
            create_post_draft(item)
            created += 1
        self.message_user(
            request,
            f'{created} draft(s) created. {skipped} skipped.',
        )
