from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from config.admin_mixins import DescriptiveAdminMixin
from .models import CuratedItem, FeedSource, LinkSubmission


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


@admin.register(LinkSubmission)
class LinkSubmissionAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'url', 'submitter_email', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'url', 'submitter_email')
    actions = ('accept_submissions', 'reject_submissions')
    readonly_fields = ('created_at', 'curated_item')

    @admin.action(description='Accept and create curated item')
    def accept_submissions(self, request, queryset):
        from .services import accept_link_submission

        count = 0
        for submission in queryset.filter(status='pending'):
            accept_link_submission(submission)
            count += 1
        self.message_user(request, f'{count} submission(s) accepted.')

    @admin.action(description='Reject selected')
    def reject_submissions(self, request, queryset):
        queryset.update(status='rejected')
