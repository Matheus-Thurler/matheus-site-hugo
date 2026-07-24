from django.contrib import admin

from config.admin_mixins import DescriptiveAdminMixin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'ip_address', 'created_at')
    actions = ('mark_read',)

    @admin.action(description='Mark as read')
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)
