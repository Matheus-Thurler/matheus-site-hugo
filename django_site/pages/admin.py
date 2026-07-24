from django.contrib import admin
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.utils.translation import gettext_lazy as _

from config.admin_mixins import DescriptiveAdminMixin
from .models import Page


class PageAdminForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = '__all__'
        widgets = {
            'content_en': CKEditorWidget(),
            'content_pt': CKEditorWidget(),
        }


@admin.register(Page)
class PageAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    form = PageAdminForm
    list_display = ('slug', 'title_en', 'is_published', 'show_in_footer', 'updated_at')
    list_filter = ('is_published', 'show_in_footer')
    prepopulated_fields = {'slug': ('title_en',)}
    search_fields = ('slug', 'title_en', 'title_pt')
    fieldsets = (
        (_('Identificação'), {'fields': ('slug', 'is_published', 'show_in_footer')}),
        (_('English'), {'fields': ('title_en', 'content_en', 'meta_description_en')}),
        (_('Português'), {'fields': ('title_pt', 'content_pt', 'meta_description_pt')}),
    )
