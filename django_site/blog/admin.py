"""Admin configuration for blog app."""
from django.contrib import admin, messages
from django.db import models
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from ckeditor.widgets import CKEditorWidget

from config.admin_mixins import DescriptiveAdminMixin
from .admin_forms import GeneratePostAIForm
from .ai_posts import create_draft_post, generate_post_payload
from .models import Author, Category, Tag, Post, Comment


@admin.register(Author)
class AuthorAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'email')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'email')


@admin.register(Category)
class CategoryAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('title_en', 'author', 'category', 'status', 'published_at', 'created_at')
    list_filter = ('status', 'category', 'created_at', 'published_at')
    search_fields = ('title_en', 'title_pt', 'description_en', 'description_pt', 'content_en', 'content_pt')
    prepopulated_fields = {'slug': ('title_en',)}
    date_hierarchy = 'published_at'
    ordering = ('-published_at',)
    change_list_template = 'admin/blog/post/change_list.html'

    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()},
    }

    fieldsets = (
        (_('Publicação'), {
            'fields': ('author', 'category', 'tags', 'slug', 'status', 'published_at'),
            'description': _('status=published + published_at define visibilidade no site.'),
        }),
        (_('English Content'), {
            'fields': ('title_en', 'description_en', 'content_en'),
            'classes': ('collapse',),
        }),
        (_('Portuguese Content'), {
            'fields': ('title_pt', 'description_pt', 'content_pt'),
            'classes': ('collapse',),
            'description': _('Deixe vazio para usar só EN ou marque use_ai_translation no admin shell.'),
        }),
        (_('SEO & Extras'), {
            'fields': ('keywords', 'cover', 'featured_image', 'show_related', 'use_ai_translation'),
            'classes': ('collapse',),
            'description': _('cover = imagem do card; featured_image = hero do post (opcional).'),
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                'generate-ai/',
                self.admin_site.admin_view(self.generate_ai_view),
                name='blog_post_generate_ai',
            ),
        ]
        return custom + urls

    def generate_ai_view(self, request):
        from django.conf import settings

        form = GeneratePostAIForm(request.POST or None)
        gemini_configured = bool(getattr(settings, 'GEMINI_API_KEY', ''))

        if request.method == 'POST' and form.is_valid() and gemini_configured:
            try:
                payload = generate_post_payload(
                    form.cleaned_data['brief'],
                    language=form.cleaned_data['language'],
                    include_code=form.cleaned_data['include_code'],
                )
                post = create_draft_post(payload, brief=form.cleaned_data['brief'])
            except Exception as exc:
                messages.error(request, _('Generation failed: %(error)s') % {'error': exc})
            else:
                messages.success(
                    request,
                    _('Draft created: %(title)s') % {'title': post.get_title()},
                )
                return redirect(reverse('admin:blog_post_change', args=[post.pk]))

        context = {
            **self.admin_site.each_context(request),
            'form': form,
            'title': _('Generate post with AI'),
            'admin_section_description': _(
                'Gera rascunho EN ou PT via Gemini. Revise tom, links e código antes de publicar.'
            ),
            'gemini_configured': gemini_configured,
            'gemini_model': getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash'),
            'opts': self.model._meta,
        }
        return render(request, 'admin/blog/generate_post_ai.html', context)


@admin.register(Comment)
class CommentAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('author', 'post', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('author__username', 'author__email', 'content', 'post__slug')
    actions = ['approve_comments', 'reject_comments']

    @admin.action(description='Approve selected comments')
    def approve_comments(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description='Reject selected comments')
    def reject_comments(self, request, queryset):
        queryset.update(status='rejected')
