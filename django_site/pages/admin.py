from django.contrib import admin
from ckeditor.widgets import CKEditorWidget
from django import forms

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
class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm
    list_display = ('slug', 'title_en', 'is_published', 'show_in_footer', 'updated_at')
    list_filter = ('is_published', 'show_in_footer')
    prepopulated_fields = {'slug': ('title_en',)}
    search_fields = ('slug', 'title_en', 'title_pt')
