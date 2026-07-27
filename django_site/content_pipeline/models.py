from django.db import models
from django.utils.translation import gettext_lazy as _


class PipelineJob(models.Model):
    """Orchestration log — curation, sync, newsletter, AI drafts."""

    JOB_TYPES = [
        ('full', _('Full pipeline')),
        ('curation', _('Curation only')),
        ('newsletter', _('Newsletter build')),
        ('sync', _('Integrations sync')),
        ('ai_draft', _('AI draft')),
    ]
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('running', _('Running')),
        ('success', _('Success')),
        ('failed', _('Failed')),
    ]

    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default='full')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    log = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Pipeline job')
        verbose_name_plural = _('Pipeline jobs')

    def __str__(self):
        return f'{self.job_type} — {self.status}'

    def append_log(self, line: str):
        self.log = (self.log + line + '\n') if self.log else line + '\n'
        self.save(update_fields=['log'])


class InstagramCarousel(models.Model):
    """Carrossel Instagram 1080×1350 — preview no admin, export/post futuro."""

    POST_TYPES = [
        ('cheatsheet', _('Cheatsheet')),
        ('tip', _('Tip')),
        ('comparison', _('Comparison')),
    ]
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('ready', _('Ready')),
        ('published', _('Published')),
    ]

    title = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Opcional — se vazio, usa o tópico.'),
    )
    topic = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Tópico'),
        help_text=_('Ex: "5 comandos kubectl essenciais" — usado pela IA para criar os slides.'),
    )
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='cheatsheet')
    slides = models.JSONField(default=list, blank=True)
    caption = models.TextField(blank=True)
    hashtags = models.JSONField(default=list, blank=True)
    cover_svg = models.TextField(blank=True)
    source_post = models.ForeignKey(
        'blog.Post',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='instagram_carousels',
        verbose_name=_('Post do blog (opcional)'),
        help_text=_('Se escolher um post, use "Gerar a partir do post" em vez do tópico.'),
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='draft')
    topic_key = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        editable=False,
        help_text=_('Assunto normalizado — evita duplicatas.'),
    )
    export_paths = models.JSONField(
        default=list,
        blank=True,
        help_text=_('Paths relativos em media/ (ex.: instagram/2/slide-01.png).'),
    )
    export_zip_path = models.CharField(
        max_length=500,
        blank=True,
        help_text=_('Path relativo do ZIP em media/ (ex.: instagram/2/carousel-2.zip).'),
    )
    exported_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = _('Carrossel Instagram')
        verbose_name_plural = _('Carrosséis Instagram')

    def __str__(self):
        return self.title or self.topic or f'Carrossel #{self.pk}'

    def save(self, *args, **kwargs):
        from content_pipeline.instagram import normalize_topic_key

        self.topic_key = normalize_topic_key(topic=self.topic or '', title=self.title or '')
        super().save(*args, **kwargs)

    @property
    def slide_count(self):
        return len(self.slides or [])

    @property
    def is_exported(self) -> bool:
        return bool(self.export_paths)

    def export_media_paths(self) -> list[str]:
        return list(self.export_paths or [])
