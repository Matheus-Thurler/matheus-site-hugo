from django.contrib import admin

from config.admin_mixins import DescriptiveAdminMixin
from .models import Redirect


@admin.register(Redirect)
class RedirectAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('old_path', 'new_path', 'is_permanent', 'created_at')
    list_filter = ('is_permanent',)
    search_fields = ('old_path', 'new_path', 'notes')
    fieldsets = (
        (None, {
            'fields': ('old_path', 'new_path', 'is_permanent', 'notes'),
            'description': 'Paths com barra inicial (/posts/foo/). 301 = permanente (SEO).',
        }),
    )
