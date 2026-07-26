from csp.decorators import csp_update
from django.conf import settings
from django.contrib import admin, messages
from django.db import connection
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from config.admin_mixins import DescriptiveAdminMixin
from .instagram import (
    caption_text,
    carousel_from_post,
    find_duplicate_carousel,
    generate_carousel_with_ai,
    slide_context,
)
from .instagram_export import InstagramExportError, export_carousel_pngs
from .models import InstagramCarousel, PipelineJob


@admin.register(PipelineJob)
class PipelineJobAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('job_type', 'status', 'started_at', 'finished_at', 'created_at')
    list_filter = ('job_type', 'status')
    readonly_fields = ('job_type', 'status', 'log', 'started_at', 'finished_at', 'created_at')

    def has_add_permission(self, request):
        return False


@admin.register(InstagramCarousel)
class InstagramCarouselAdmin(DescriptiveAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'post_type', 'status', 'slide_count', 'updated_at', 'preview_link')
    list_filter = ('post_type', 'status')
    search_fields = ('title', 'topic', 'caption')
    readonly_fields = ('created_at', 'updated_at', 'preview_link', 'export_files_display', 'topic_key')
    autocomplete_fields = ('source_post',)
    change_form_template = 'admin/content_pipeline/instagramcarousel/change_form.html'
    change_list_template = 'admin/content_pipeline/instagramcarousel/change_list.html'
    actions = ('generate_with_ai', 'generate_from_post')

    fieldsets = (
        (_('Passo 1 — Defina o conteúdo'), {
            'fields': ('topic', 'title', 'post_type', 'source_post', 'status'),
            'description': _(
                'Basta o Tópico (ex: "5 comandos kubectl") e clicar em Ver preview — '
                'a IA gera os slides automaticamente (~15s).'
            ),
        }),
        (_('Passo 2 — Slides (preenchido pela IA)'), {
            'fields': ('slides', 'cover_svg', 'caption', 'hashtags'),
            'classes': ('collapse',),
            'description': _('Avançado — normalmente a IA preenche. Edite só se quiser ajustar um slide.'),
        }),
        (_('Exportação PNG'), {
            'fields': ('export_files_display', 'exported_at', 'export_paths'),
            'classes': ('collapse',),
            'description': _('PNG 1080×1350 salvos em media/instagram/&lt;id&gt;/ — prontos para postar no Instagram.'),
        }),
        (_('Preview'), {
            'fields': ('preview_link',),
            'description': _('Com tópico preenchido, use "Ver preview →" no rodapé — gera e abre de uma vez.'),
        }),
        (_('Meta'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description=_('Slides'))
    def slide_count(self, obj):
        return obj.slide_count

    @admin.display(description=_('Preview'))
    def preview_link(self, obj):
        if obj is None or not obj.pk:
            return mark_safe(
                '<span class="quiet">Preencha o tópico e clique em <strong>Ver preview →</strong> no rodapé.</span>'
            )
        url = reverse('admin:content_pipeline_instagramcarousel_preview', args=[obj.pk])
        if obj.slide_count:
            label = 'Abrir preview'
        elif obj.topic or obj.title or obj.source_post_id:
            label = 'Gerar e abrir preview'
        else:
            return mark_safe(
                '<span class="quiet">Preencha o Tópico e use o botão no rodapé.</span>'
            )
        return format_html(
            '<a class="button" href="{}?autogenerate=1" target="_blank">{}</a>',
            url,
            label,
        )

    @admin.display(description=_('PNGs exportados'))
    def export_files_display(self, obj):
        if not obj or not obj.export_paths:
            return mark_safe('<span class="quiet">Nenhum PNG exportado ainda.</span>')
        links = []
        for rel in obj.export_paths:
            url = f'{settings.MEDIA_URL.rstrip("/")}/{rel}'
            name = rel.rsplit('/', 1)[-1]
            links.append(f'<a href="{url}" target="_blank">{name}</a>')
        exported = obj.exported_at.strftime('%d/%m/%Y %H:%M') if obj.exported_at else '—'
        return mark_safe(f'<div class="mb-1">{" · ".join(links)}</div><small class="quiet">Exportado em {exported}</small>')

    def _duplicate_warning(self, request, obj):
        dup = find_duplicate_carousel(
            topic=obj.topic or '',
            title=obj.title or '',
            exclude_pk=obj.pk,
        )
        if dup:
            url = reverse('admin:content_pipeline_instagramcarousel_change', args=[dup.pk])
            messages.warning(
                request,
                format_html(
                    'Já existe carrossel sobre este assunto: <a href="{}">#{} — {}</a>',
                    url,
                    dup.pk,
                    dup.title or dup.topic,
                ),
            )
            return dup
        return None

    def _block_if_duplicate(self, request, obj):
        dup = find_duplicate_carousel(
            topic=obj.topic or '',
            title=obj.title or '',
            exclude_pk=obj.pk,
        )
        if dup:
            url = reverse('admin:content_pipeline_instagramcarousel_change', args=[dup.pk])
            messages.error(
                request,
                format_html(
                    'Assunto duplicado — use o carrossel existente: <a href="{}">#{}</a>',
                    url,
                    dup.pk,
                ),
            )
            return True
        return False

    def _run_export_pngs(self, request, carousel):
        try:
            paths = export_carousel_pngs(carousel)
        except InstagramExportError as exc:
            messages.error(request, str(exc))
            return False
        messages.success(request, f'{len(paths)} PNG(s) exportados para media/instagram/{carousel.pk}/')
        return True

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            return [fs for fs in fieldsets if fs[0] not in (_('Preview'), _('Meta'))]
        return fieldsets

    def _redirect_preview(self, request, obj):
        if self._block_if_duplicate(request, obj):
            return redirect('admin:content_pipeline_instagramcarousel_change', obj.pk)
        if not self._ensure_slides(request, obj):
            return redirect('admin:content_pipeline_instagramcarousel_change', obj.pk)
        messages.success(request, f'Preview pronto — {obj.slide_count} slides.')
        return redirect('admin:content_pipeline_instagramcarousel_preview', obj.pk)

    def _apply_ai_data(self, carousel, data):
        carousel.title = data.get('title', carousel.title)[:255]
        carousel.slides = data.get('slides', [])
        carousel.caption = data.get('caption', '')
        carousel.hashtags = data.get('hashtags', [])
        carousel.cover_svg = data.get('cover_svg', '')
        carousel.save()

    def save_model(self, request, obj, form, change):
        if not (obj.title or '').strip() and (obj.topic or '').strip():
            obj.title = obj.topic.strip()[:255]
        if not (obj.topic or '').strip() and (obj.title or '').strip():
            obj.topic = obj.title.strip()[:255]
        super().save_model(request, obj, form, change)
        self._duplicate_warning(request, obj)

    def _run_generate_ai(self, request, carousel, *, quiet=False):
        topic = (carousel.topic or carousel.title or '').strip()
        if not topic:
            messages.error(request, 'Preencha o campo Tópico antes de gerar.')
            return False
        if not quiet and self._block_if_duplicate(request, carousel):
            return False
        connection.close()
        try:
            data = generate_carousel_with_ai(topic, carousel.post_type)
        except Exception as exc:
            messages.error(request, f'Erro na IA: {exc}')
            return False
        self._apply_ai_data(carousel, data)
        if not quiet:
            messages.success(request, f'{carousel.slide_count} slides gerados.')
        return True

    def _run_generate_from_post(self, request, carousel, *, quiet=False):
        if not carousel.source_post:
            messages.error(request, 'Selecione um Post do blog ou use o campo Tópico.')
            return False
        if not quiet and self._block_if_duplicate(request, carousel):
            return False
        connection.close()
        try:
            data = carousel_from_post(carousel.source_post, carousel.post_type)
        except Exception as exc:
            messages.error(request, f'Erro na IA: {exc}')
            return False
        self._apply_ai_data(carousel, data)
        if not quiet:
            messages.success(request, f'{carousel.slide_count} slides gerados a partir do post.')
        return True

    def _ensure_slides(self, request, carousel):
        """Gera slides automaticamente se ainda não existirem."""
        if carousel.slide_count:
            return True
        if carousel.source_post_id:
            return self._run_generate_from_post(request, carousel, quiet=True)
        return self._run_generate_ai(request, carousel, quiet=True)

    @admin.action(description=_('Gerar slides com IA (campo tópico)'))
    def generate_with_ai(self, request, queryset):
        updated = 0
        for carousel in queryset:
            if self._run_generate_ai(request, carousel):
                updated += 1
        if updated:
            messages.info(request, 'Abra cada carrossel e clique em "Ver preview →".')

    @admin.action(description=_('Gerar a partir do post vinculado'))
    def generate_from_post(self, request, queryset):
        updated = 0
        for carousel in queryset:
            if self._run_generate_from_post(request, carousel):
                updated += 1
        if updated:
            messages.info(request, 'Abra cada carrossel e clique em "Ver preview →".')

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                '<int:pk>/preview/',
                self.admin_site.admin_view(self.preview_view),
                name='content_pipeline_instagramcarousel_preview',
            ),
            path(
                '<int:pk>/slide/<int:slide_num>/',
                csp_update({'frame-ancestors': ["'self'"]})(
                    self.admin_site.admin_view(self.slide_view)
                ),
                name='content_pipeline_instagramcarousel_slide',
            ),
        ]
        return custom + urls

    def preview_view(self, request, pk):
        carousel = get_object_or_404(InstagramCarousel, pk=pk)
        if request.GET.get('autogenerate') and not carousel.slide_count:
            if not self._ensure_slides(request, carousel):
                return redirect('admin:content_pipeline_instagramcarousel_change', pk)
            carousel.refresh_from_db()

        if not carousel.slide_count:
            messages.warning(request, 'Preencha o Tópico e clique em Ver preview.')
            return redirect('admin:content_pipeline_instagramcarousel_change', pk)

        slide_num = int(request.GET.get('slide', 1))
        slide_num = max(1, min(slide_num, carousel.slide_count))

        context = {
            **self.admin_site.each_context(request),
            'carousel': carousel,
            'slide_num': slide_num,
            'caption': caption_text(carousel),
            'title': f'Preview — {carousel.title}',
            'has_exports': bool(carousel.export_paths),
            **slide_context(carousel, slide_num - 1),
        }
        return render(request, 'admin/content_pipeline/instagram_preview.html', context)

    def slide_view(self, request, pk, slide_num):
        carousel = get_object_or_404(InstagramCarousel, pk=pk)
        context = slide_context(carousel, slide_num - 1)
        response = render(request, 'social/instagram/slide.html', context)
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response

    def response_change(self, request, obj):
        if '_generate_ai' in request.POST:
            self._run_generate_ai(request, obj)
            return redirect('admin:content_pipeline_instagramcarousel_change', obj.pk)
        if '_generate_from_post' in request.POST:
            self._run_generate_from_post(request, obj)
            return redirect('admin:content_pipeline_instagramcarousel_change', obj.pk)
        if '_export_pngs' in request.POST:
            self._run_export_pngs(request, obj)
            return redirect('admin:content_pipeline_instagramcarousel_change', obj.pk)
        if '_preview' in request.POST:
            return self._redirect_preview(request, obj)
        return super().response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        if '_generate_ai' in request.POST:
            self._run_generate_ai(request, obj)
            return redirect('admin:content_pipeline_instagramcarousel_change', obj.pk)
        if '_generate_from_post' in request.POST:
            self._run_generate_from_post(request, obj)
            return redirect('admin:content_pipeline_instagramcarousel_change', obj.pk)
        if '_export_pngs' in request.POST:
            self._run_export_pngs(request, obj)
            return redirect('admin:content_pipeline_instagramcarousel_change', obj.pk)
        if '_preview' in request.POST:
            return self._redirect_preview(request, obj)
        return super().response_add(request, obj, post_url_continue)

    class Media:
        css = {'all': ('css/admin.css',)}
