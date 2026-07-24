import csv

from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from config.admin_mixins import DescriptiveAdminMixin
from .models import Subscriber


@admin.action(description=_('Export selected to CSV'))
def export_csv_action(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'
    writer = csv.writer(response)
    writer.writerow(['email', 'name', 'language', 'subscribed_at', 'is_active'])
    for sub in queryset:
        writer.writerow([
            sub.email,
            sub.name,
            sub.language,
            sub.subscribed_at.isoformat(),
            sub.is_active,
        ])
    return response


@admin.action(description=_('Deactivate selected subscribers'))
def deactivate_subscribers(modeladmin, request, queryset):
    updated = queryset.filter(is_active=True).update(is_active=False)
    messages.success(request, _('Deactivated %(count)d subscriber(s).') % {'count': updated})


@admin.register(Subscriber)
class SubscriberAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('email', 'name', 'language', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'language', 'subscribed_at')
    search_fields = ('email', 'name')
    readonly_fields = ('subscribed_at', 'unsubscribed_at', 'unsubscribe_token')
    actions = [export_csv_action, deactivate_subscribers]
    ordering = ('-subscribed_at',)

    @admin.display(description=_('Unsubscribe token'))
    def unsubscribe_token(self, obj):
        return obj.unsubscribe_token
