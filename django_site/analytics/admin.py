from django.contrib import admin
from django.db.models import Count

from config.admin_mixins import DescriptiveAdminMixin
from .models import PageView


@admin.register(PageView)
class PageViewAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('path', 'post_slug', 'referrer', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('path', 'post_slug', 'referrer')
    readonly_fields = ('path', 'referrer', 'visitor_hash', 'post_slug', 'created_at')
    date_hierarchy = 'created_at'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        top = (
            PageView.objects.values('path')
            .annotate(views=Count('id'))
            .order_by('-views')[:10]
        )
        extra_context['top_pages'] = top
        extra_context['total_views'] = PageView.objects.count()
        return super().changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
