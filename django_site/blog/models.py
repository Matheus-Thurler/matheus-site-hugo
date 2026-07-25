from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    """Author/Profile model."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    content_teaching = models.TextField(blank=True, help_text=_('Content & Teaching section text'))
    goals = models.TextField(blank=True, help_text=_('Current Goals - one per line'))
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    github = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:about')


class Category(models.Model):
    """Category model."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})


class Tag(models.Model):
    """Tag model."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:tag', kwargs={'slug': self.slug})


class PostManager(models.Manager):
    """Custom manager for Post model."""

    def published(self):
        return self.filter(status='published').select_related('author')

    def get_queryset(self):
        return super().get_queryset().select_related('author')


class Post(models.Model):
    """Blog post model with i18n support."""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
    ]

    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')

    # Common fields
    slug = models.SlugField(max_length=255, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    # English content
    title_en = models.CharField(max_length=255, blank=True)
    description_en = models.TextField(blank=True)
    content_en = models.TextField(blank=True)

    # Portuguese content
    title_pt = models.CharField(max_length=255, blank=True)
    description_pt = models.TextField(blank=True)
    content_pt = models.TextField(blank=True)

    # Auto-translated fallback (if using AI translation)
    use_ai_translation = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # SEO & extras
    keywords = models.CharField(max_length=500, blank=True)
    cover = models.CharField(
        max_length=500,
        blank=True,
        help_text=_('Cover image path (/images/covers/...) or external URL'),
    )
    featured_image = models.ImageField(upload_to='posts/', blank=True)
    show_related = models.BooleanField(default=True)
    reading_time = models.PositiveIntegerField(default=0, help_text=_('Estimated reading time in minutes'))
    content_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When the post content was last meaningfully updated'),
    )
    show_updated_badge = models.BooleanField(default=False)
    youtube_video_id = models.CharField(max_length=20, blank=True)
    og_title_en = models.CharField(max_length=255, blank=True)
    og_title_pt = models.CharField(max_length=255, blank=True)
    og_description_en = models.TextField(blank=True)
    og_description_pt = models.TextField(blank=True)
    crosspost_linkedin = models.TextField(blank=True)
    crosspost_mastodon = models.TextField(blank=True)
    crosspost_telegram = models.TextField(blank=True)

    objects = PostManager()

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ['-published_at']

    def __str__(self):
        return self.title_en or self.title_pt or self.slug

    @staticmethod
    def _resolve_lang(lang=None):
        if lang is not None:
            return lang if lang in ('en', 'pt') else 'en'
        from django.utils.translation import get_language
        active = get_language()
        return active if active in ('en', 'pt') else 'en'

    def get_title(self, lang=None):
        """Get title based on language, with fallback."""
        lang = self._resolve_lang(lang)
        if lang == 'en':
            return self.title_en or self.title_pt or self.slug
        return self.title_pt or self.title_en or self.slug

    def get_description(self, lang=None):
        """Get description based on language, with fallback."""
        lang = self._resolve_lang(lang)
        if lang == 'en':
            return self.description_en or self.description_pt or ''
        return self.description_pt or self.description_en or ''

    def get_content(self, lang=None):
        """Get content based on language, with fallback."""
        lang = self._resolve_lang(lang)
        if lang == 'en':
            return self.content_en or self.content_pt or ''
        return self.content_pt or self.content_en or ''

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    @property
    def cover_url(self):
        """Resolve cover URL from Hugo frontmatter, static files, or media."""
        from django.templatetags.static import static

        raw = (self.cover or '').strip()
        if not raw and self.featured_image:
            raw = str(self.featured_image).strip()

        if not raw:
            return ''

        if raw.startswith('http://') or raw.startswith('https://'):
            return raw

        path = raw.lstrip('/')
        static_root = settings.BASE_DIR / 'static'
        stem = path.rsplit('.', 1)[0] if '.' in path else path
        extensions = ('webp', 'png', 'jpg', 'jpeg')
        for ext in extensions:
            candidate = f'{stem}.{ext}'
            if (static_root / candidate).exists():
                return static(candidate)

        if settings.DEBUG and self.featured_image:
            try:
                return self.featured_image.url
            except ValueError:
                pass

        return static(path) if (static_root / path).exists() else ''

    def save(self, *args, **kwargs):
        content = self.content_en or self.content_pt or ''
        words = len(content.split())
        self.reading_time = max(1, words // 200)
        if self.pk:
            old = Post.objects.filter(pk=self.pk).values(
                'content_en', 'content_pt',
            ).first()
            if old and (
                old['content_en'] != self.content_en
                or old['content_pt'] != self.content_pt
            ):
                from django.utils import timezone
                self.content_updated_at = timezone.now()
        super().save(*args, **kwargs)

    def get_og_title(self, lang=None):
        lang = self._resolve_lang(lang)
        if lang == 'pt' and self.og_title_pt:
            return self.og_title_pt
        if self.og_title_en:
            return self.og_title_en
        return self.get_title(lang)

    def get_og_description(self, lang=None):
        lang = self._resolve_lang(lang)
        if lang == 'pt' and self.og_description_pt:
            return self.og_description_pt
        if self.og_description_en:
            return self.og_description_en
        return self.get_description(lang)


class Comment(models.Model):
    """Comment model for blog posts."""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author} - {self.post.slug}"


class Series(models.Model):
    """Ordered learning path grouping related posts."""

    slug = models.SlugField(max_length=120, unique=True)
    title_en = models.CharField(max_length=255)
    title_pt = models.CharField(max_length=255, blank=True)
    description_en = models.TextField(blank=True)
    description_pt = models.TextField(blank=True)
    cover = models.CharField(max_length=500, blank=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    posts = models.ManyToManyField(
        Post,
        through='SeriesPost',
        related_name='series_list',
        blank=True,
    )

    class Meta:
        verbose_name = _('Series')
        verbose_name_plural = _('Series')
        ordering = ['order', 'slug']

    def __str__(self):
        return self.title_en or self.slug

    def get_title(self, lang=None):
        lang = Post._resolve_lang(lang)
        if lang == 'pt':
            return self.title_pt or self.title_en
        return self.title_en

    def get_description(self, lang=None):
        lang = Post._resolve_lang(lang)
        if lang == 'pt':
            return self.description_pt or self.description_en
        return self.description_en

    def get_absolute_url(self):
        return reverse('blog:series_detail', kwargs={'slug': self.slug})


class SeriesPost(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='series_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='series_memberships')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = [('series', 'post')]

    def __str__(self):
        return f'{self.series.slug} → {self.post.slug}'


class PostFeedback(models.Model):
    """Anonymous helpful / not helpful votes on posts."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='feedback')
    helpful = models.BooleanField()
    visitor_hash = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('post', 'visitor_hash')]
        verbose_name = _('Post feedback')
        verbose_name_plural = _('Post feedback')

    def __str__(self):
        label = 'helpful' if self.helpful else 'not helpful'
        return f'{self.post.slug} — {label}'


class ProfileLink(models.Model):
    """Editable link for the /links/ link-in-bio page."""

    SECTION_CARD = 'card'
    SECTION_SOCIAL = 'social'
    SECTION_CHOICES = [
        (SECTION_CARD, _('Card principal')),
        (SECTION_SOCIAL, _('Ícone social (rodapé)')),
    ]

    section = models.CharField(
        max_length=10,
        choices=SECTION_CHOICES,
        default=SECTION_CARD,
        help_text=_('Cards aparecem na lista; ícones sociais ficam na fileira inferior.'),
    )
    title_en = models.CharField(max_length=200, blank=True)
    title_pt = models.CharField(max_length=200, blank=True)
    description_en = models.CharField(max_length=300, blank=True)
    description_pt = models.CharField(max_length=300, blank=True)
    url = models.CharField(
        max_length=500,
        blank=True,
        help_text=_('URL externa, mailto: ou caminho (/about/). Deixe vazio se usar rota interna.'),
    )
    internal_route = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Nome de rota Django (ex.: blog:home). Tem prioridade sobre URL.'),
    )
    external = models.BooleanField(
        default=True,
        help_text=_('Abre em nova aba quando marcado.'),
    )
    image = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Ícone PNG em static/ (ex.: images/icons/youtube.png).'),
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Ícone SVG: posts, github, youtube, linkedin, email.'),
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Link da página /links/')
        verbose_name_plural = _('Links da página /links/')
        ordering = ['section', 'order', 'pk']

    def __str__(self):
        label = self.title_pt or self.title_en or self.url or self.internal_route
        return f"{label} ({self.get_section_display()})"
