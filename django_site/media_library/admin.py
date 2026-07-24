from django.contrib import admin

from config.admin_mixins import DescriptiveAdminMixin
from .models import MediaAsset


@admin.register(MediaAsset)
class MediaAssetAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'file', 'uploaded_at')
    search_fields = ('title', 'alt_text', 'tags', 'caption')
    list_filter = ('uploaded_at',)
