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
from .models import Author, Category, Tag, Post, Comment, ProfileLink, Series, SeriesPost, PostFeedback


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
            'fields': (
                'keywords', 'cover', 'featured_image', 'show_related', 'use_ai_translation',
                'content_updated_at', 'show_updated_badge', 'youtube_video_id',
                'og_title_en', 'og_title_pt', 'og_description_en', 'og_description_pt',
                'crosspost_linkedin', 'crosspost_mastodon', 'crosspost_telegram',
            ),
            'classes': ('collapse',),
            'description': _('cover = imagem do card; featured_image = hero do post (opcional).'),
        }),
    )
    actions = (
        'translate_to_pt',
        'translate_to_en',
        'generate_seo_meta',
        'generate_crosspost_drafts',
        'suggest_youtube_links',
    )

    @admin.action(description='Translate to Portuguese (AI)')
    def translate_to_pt(self, request, queryset):
        self._run_translation(request, queryset, 'pt')

    @admin.action(description='Translate to English (AI)')
    def translate_to_en(self, request, queryset):
        self._run_translation(request, queryset, 'en')

    def _run_translation(self, request, queryset, target_lang):
        from blog.platform import translate_post_with_ai

        updated = 0
        for post in queryset:
            try:
                data = translate_post_with_ai(post, target_lang)
            except Exception as exc:
                messages.error(request, f'{post.slug}: {exc}')
                continue
            if target_lang == 'pt':
                post.title_pt = data.get('title', '')[:255]
                post.description_pt = data.get('description', '')
                post.content_pt = data.get('content', '')
            else:
                post.title_en = data.get('title', '')[:255]
                post.description_en = data.get('description', '')
                post.content_en = data.get('content', '')
            post.save()
            updated += 1
        messages.success(request, f'{updated} post(s) translated.')

    @admin.action(description='Generate SEO meta (AI)')
    def generate_seo_meta(self, request, queryset):
        from blog.platform import generate_seo_meta

        updated = 0
        for post in queryset:
            try:
                data = generate_seo_meta(post)
            except Exception as exc:
                messages.error(request, f'{post.slug}: {exc}')
                continue
            post.og_title_en = data.get('og_title_en', '')[:255]
            post.og_title_pt = data.get('og_title_pt', '')[:255]
            post.og_description_en = data.get('og_description_en', '')
            post.og_description_pt = data.get('og_description_pt', '')
            if data.get('keywords'):
                post.keywords = data['keywords'][:500]
            post.save()
            updated += 1
        messages.success(request, f'SEO meta generated for {updated} post(s).')

    @admin.action(description='Generate cross-post drafts (AI)')
    def generate_crosspost_drafts(self, request, queryset):
        from blog.platform import generate_crosspost_drafts

        updated = 0
        for post in queryset:
            try:
                data = generate_crosspost_drafts(post)
            except Exception as exc:
                messages.error(request, f'{post.slug}: {exc}')
                continue
            post.crosspost_linkedin = data.get('linkedin', '')
            post.crosspost_mastodon = data.get('mastodon', '')
            post.crosspost_telegram = data.get('telegram', '')
            post.save(update_fields=[
                'crosspost_linkedin', 'crosspost_mastodon', 'crosspost_telegram',
            ])
            updated += 1
        messages.success(request, f'Cross-post drafts generated for {updated} post(s).')

    @admin.action(description='Suggest YouTube video links')
    def suggest_youtube_links(self, request, queryset):
        from blog.platform import match_youtube_videos_to_posts

        suggestions = {s['post_slug']: s for s in match_youtube_videos_to_posts()}
        updated = 0
        for post in queryset:
            suggestion = suggestions.get(post.slug)
            if suggestion and not post.youtube_video_id:
                post.youtube_video_id = suggestion['video_id']
                post.save(update_fields=['youtube_video_id'])
                updated += 1
        messages.success(request, f'YouTube IDs applied to {updated} post(s).')

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
            'gemini_model': getattr(settings, 'GEMINI_MODEL', 'gemini-3.5-flash'),
            'opts': self.model._meta,
        }
        return render(request, 'admin/blog/generate_post_ai.html', context)


class SeriesPostInline(admin.TabularInline):
    model = SeriesPost
    extra = 1
    ordering = ('order',)


@admin.register(Series)
class SeriesAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('title_en', 'slug', 'is_published', 'order')
    prepopulated_fields = {'slug': ('title_en',)}
    inlines = (SeriesPostInline,)


@admin.register(PostFeedback)
class PostFeedbackAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('post', 'helpful', 'created_at')
    list_filter = ('helpful', 'created_at')
    readonly_fields = ('post', 'helpful', 'visitor_hash', 'created_at')

    def has_add_permission(self, request):
        return False


@admin.register(Comment)
class CommentAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('author', 'post', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('author__username', 'author__email', 'content', 'post__slug')
    actions = ['approve_comments', 'reject_comments', 'moderate_with_ai']

    @admin.action(description='Moderate with AI')
    def moderate_with_ai(self, request, queryset):
        from blog.platform import moderate_comment_with_ai

        for comment in queryset.filter(status='pending'):
            try:
                result = moderate_comment_with_ai(comment)
            except Exception as exc:
                messages.error(request, f'Comment #{comment.pk}: {exc}')
                continue
            comment.status = 'approved' if result.get('approve') else 'rejected'
            comment.save(update_fields=['status'])
        messages.success(request, 'AI moderation completed.')

    @admin.action(description='Approve selected comments')
    def approve_comments(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description='Reject selected comments')
    def reject_comments(self, request, queryset):
        queryset.update(status='rejected')


@admin.register(ProfileLink)
class ProfileLinkAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('title_en', 'section', 'url', 'internal_route', 'order', 'is_active')
    list_filter = ('section', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title_en', 'title_pt', 'url', 'internal_route')
    ordering = ('section', 'order', 'pk')
    fieldsets = (
        (_('Visibilidade'), {
            'fields': ('section', 'order', 'is_active'),
            'description': _('Ordem menor aparece primeiro. Desative sem apagar.'),
        }),
        (_('Textos'), {
            'fields': ('title_en', 'title_pt', 'description_en', 'description_pt'),
            'description': _('Cards usam título e descrição; ícones sociais usam só o título como tooltip.'),
        }),
        (_('Destino'), {
            'fields': ('url', 'internal_route', 'external'),
            'description': _(
                'Use internal_route para páginas do site (ex.: blog:home). '
                'Para YouTube, GitHub etc., preencha url.'
            ),
        }),
        (_('Ícone'), {
            'fields': ('image', 'icon'),
            'description': _(
                'Cards: PNG em static (image) ou ícone SVG (icon). '
                'Ícones sociais: preencha icon (github, youtube, linkedin, email).'
            ),
        }),
    )
