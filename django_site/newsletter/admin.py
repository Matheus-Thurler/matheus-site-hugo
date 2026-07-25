from django.contrib import admin

from config.admin_mixins import DescriptiveAdminMixin
from .models import LeadMagnet, Subscriber


@admin.register(Subscriber)
class SubscriberAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('email', 'name', 'language', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'language')
    search_fields = ('email', 'name')
    actions = ('export_csv_action', 'deactivate_subscribers')

    @admin.action(description='Export selected to CSV')
    def export_csv_action(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'
        writer = csv.writer(response)
        writer.writerow(['email', 'name', 'language'])
        for sub in queryset:
            writer.writerow([sub.email, sub.name, sub.language])
        return response

    @admin.action(description='Deactivate selected')
    def deactivate_subscribers(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(LeadMagnet)
class LeadMagnetAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('title_en', 'slug', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('title_en',)}
    search_fields = ('title_en', 'title_pt', 'slug')
