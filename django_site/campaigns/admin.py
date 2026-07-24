from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from config.admin_mixins import DescriptiveAdminMixin
from .models import NewsletterCampaign
from .services import send_campaign


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('subject_pt', 'status', 'recipient_count', 'sent_at', 'created_at')
    list_filter = ('status',)
    readonly_fields = ('sent_at', 'recipient_count', 'discord_message_id', 'discord_channel_id', 'created_at')
    actions = ('send_now', 'post_to_discord_review')
    fieldsets = (
        (_('Assunto'), {'fields': ('subject_en', 'subject_pt')}),
        (_('Conteúdo'), {
            'fields': ('body_markdown', 'body_html_en', 'body_html_pt'),
            'description': _('body_markdown = rascunho semanal da curadoria (PT). HTML gerado na aprovação.'),
        }),
        (_('Envio & Discord'), {
            'fields': ('status', 'scheduled_at', 'sent_at', 'recipient_count', 'discord_message_id', 'discord_channel_id'),
        }),
    )

    @admin.action(description='Send campaign now (skip Discord review)')
    def send_now(self, request, queryset):
        total = 0
        for campaign in queryset.exclude(status='sent'):
            total += send_campaign(campaign)
        self.message_user(request, f'Sent to {total} recipients.', messages.SUCCESS)

    @admin.action(description='Post to Discord for review')
    def post_to_discord_review(self, request, queryset):
        from discord_bot.client import post_draft_for_review

        for campaign in queryset.filter(status__in=('draft', 'pending_review')):
            msg = post_draft_for_review(campaign)
            campaign.discord_message_id = str(msg['id'])
            campaign.discord_channel_id = str(msg.get('channel_id', ''))
            campaign.status = 'pending_review'
            campaign.save(update_fields=['discord_message_id', 'discord_channel_id', 'status'])
        self.message_user(request, 'Posted to Discord #drafts-review.', messages.SUCCESS)
