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
        # Auto-calculate reading time
        content = self.content_en or self.content_pt or ''
        words = len(content.split())
        self.reading_time = max(1, words // 200)  # ~200 words per minute
        super().save(*args, **kwargs)


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
