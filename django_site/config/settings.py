"""
Django settings for Matheus Thurler Blog.
"""

from pathlib import Path
import json
import os

from dotenv import load_dotenv

from config.gcp_secrets import get_secret

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env', override=True)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-dev-key-change-in-production'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

_csrf_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_origins.split(',') if o.strip()]

# Canonical public URL (SEO, prerender, absolute links)
SITE_CANONICAL_HOST = os.environ.get('SITE_CANONICAL_HOST', 'matheusthurler.com.br')
SITE_CANONICAL_URL = os.environ.get(
    'SITE_CANONICAL_URL',
    f'https://{SITE_CANONICAL_HOST}',
).rstrip('/')

for _site_host in (SITE_CANONICAL_HOST, f'www.{SITE_CANONICAL_HOST}'):
    if _site_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_site_host)


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'ckeditor',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',
    # Security
    'axes',
    'csp',
    # Local apps
    'blog',
    'newsletter',
    'redirects',
    'pages',
    'media_library',
    'contact',
    'analytics',
    'curation',
    'campaigns',
    'content_pipeline',
    'integrations',
    'discord_bot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'csp.middleware.CSPMiddleware',  # CSP header handling
    'axes.middleware.AxesMiddleware',  # Brute force protection
    'django.contrib.sessions.middleware.SessionMiddleware',
    'redirects.middleware.RedirectMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # i18n
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'blog.performance.PublicCacheMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'blog.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database — DB_ENGINE=sqlite (default) or postgresql
DB_ENGINE = os.environ.get('DB_ENGINE', 'sqlite').lower()

if DB_ENGINE == 'postgresql':
    _pg_host = os.environ.get('POSTGRES_HOST', 'db')
    _pg_port = os.environ.get('POSTGRES_PORT', '5432')
    if _pg_host.startswith('/cloudsql'):
        _pg_port = ''

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'blog'),
            'USER': os.environ.get('POSTGRES_USER', 'blog'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'blog'),
            'HOST': _pg_host,
            'PORT': _pg_port,
            'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '60')),
            'OPTIONS': {
                'connect_timeout': 10,
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': Path(os.environ.get('DATABASE_PATH', BASE_DIR / 'db.sqlite3')),
            'OPTIONS': {
                'timeout': 30,
            },
        }
    }

    from django.db.backends.signals import connection_created

    def _sqlite_wal(sender, connection, **kwargs):
        if connection.vendor == 'sqlite':
            with connection.cursor() as cursor:
                cursor.execute('PRAGMA journal_mode=WAL;')
                cursor.execute('PRAGMA busy_timeout=30000;')

    connection_created.connect(_sqlite_wal)


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'en-us'

LANGUAGES = [
    ('en', 'English'),
    ('pt', 'Português'),
]

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': (
            'django.contrib.staticfiles.storage.StaticFilesStorage'
            if DEBUG
            else 'whitenoise.storage.CompressedStaticFilesStorage'
        ),
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Site ID for django.contrib.sites
SITE_ID = 1

# Authentication backends (django-axes + allauth)
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'config.auth_backends.EmailOrUsernameBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Login/logout redirects
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# django-allauth settings
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

# Social account settings
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'


# Site settings (from Hugo config)
SITE_NAME = 'Matheus Thurler'
SITE_DESCRIPTION = 'DevOps & Platform Engineer focused on Google Cloud. Tutorials, articles, and content about Kubernetes, Terraform, CI/CD, SRE, and Platform Engineering.'
SITE_KEYWORDS = ['DevOps', 'Google Cloud', 'GCP', 'Kubernetes', 'Terraform', 'Platform Engineering', 'SRE', 'CI/CD']

# Author info
AUTHOR_NAME = 'Matheus Thurler'
AUTHOR_TITLE = 'DevOps & Platform Engineer | Creator of VirtFoundry'
AUTHOR_DESCRIPTION = (
    'DevOps & Platform Engineer focused on Google Cloud, Infrastructure as Code, and SRE. '
    'Creator of VirtFoundry — an open-source Kubernetes-native IaaS control plane on KubeVirt.'
)
AUTHOR_CONTENT_TEACHING = 'I create tutorials and educational content about DevOps, Cloud Native technologies, and Platform Engineering. My goal is to help others learn complex topics through practical, real-world examples.'
AUTHOR_GOALS = (
    'Growing VirtFoundry as open-source KubeVirt IaaS\n'
    'Google Cloud Innovator program\n'
    'Contributing to open source projects\n'
    'Building a community around Platform Engineering\n'
    'Learning and sharing about AI/LLM integration in DevOps workflows'
)
AUTHOR_GITHUB = 'https://github.com/Matheus-Thurler'
AUTHOR_YOUTUBE = 'https://youtube.com/@matheusthurler'
AUTHOR_LINKEDIN = 'https://linkedin.com/in/matheusthurler'
AUTHOR_EMAIL = 'matheus@matheusthurler.com.br'
AUTHOR_AVATAR = 'images/avatar.png'
AUTHOR_LINKS_SUBTITLE = 'DevOps Engineer & Content Creator'
VIRTFOUNDRY_URL = 'https://github.com/virtfoundry'

AUTHOR_SOCIAL = [
    {'name': 'GitHub', 'url': AUTHOR_GITHUB, 'icon': 'github'},
    {'name': 'YouTube', 'url': AUTHOR_YOUTUBE, 'icon': 'youtube'},
    {'name': 'LinkedIn', 'url': AUTHOR_LINKEDIN, 'icon': 'linkedin'},
    {'name': 'Email', 'url': f'mailto:{AUTHOR_EMAIL}', 'icon': 'email'},
]

# Highlighted on /projects/ (org lives under github.com/virtfoundry)
FEATURED_PROJECTS = [
    {
        'name': 'VirtFoundry',
        'description': (
            'Open-source Kubernetes-native IaaS control plane on KubeVirt — '
            'multi-tenant VMs, networking, and a CloudStack-inspired API.'
        ),
        'url': 'https://github.com/virtfoundry',
        'language': 'Go',
        'role': 'Creator',
        'stars': None,
    },
    {
        'name': 'virtfoundry/core',
        'description': 'API, worker, and UI for the VirtFoundry control plane.',
        'url': 'https://github.com/virtfoundry/core',
        'language': 'Go',
        'role': 'Creator',
        'stars': None,
    },
    {
        'name': 'virtfoundry/helm-charts',
        'description': 'Helm charts and docs to install VirtFoundry on Kubernetes.',
        'url': 'https://github.com/virtfoundry/helm-charts',
        'language': 'YAML',
        'role': 'Creator',
        'stars': None,
    },
]

LINKS_PAGE_PT = [
    {
        'title': 'Canal no YouTube',
        'description': 'Vídeos sobre DevOps, Kubernetes e Homelab',
        'url': 'https://youtube.com/@matheusthurler',
        'image': 'images/icons/youtube.png',
        'external': True,
    },
    {
        'title': 'Blog',
        'description': 'Artigos técnicos sobre tecnologia',
        'url_name': 'blog:home',
        'icon': 'posts',
        'external': False,
    },
    {
        'title': 'LinkedIn',
        'description': 'Meu perfil profissional',
        'url': 'https://linkedin.com/in/matheus-thurler',
        'image': 'images/icons/linkedin.png',
        'external': True,
    },
    {
        'title': 'Instagram',
        'description': '@maththurler.devops',
        'url': 'https://instagram.com/maththurler.devops',
        'image': 'images/icons/instagram.png',
        'external': True,
    },
    {
        'title': 'TikTok',
        'description': '@matheusthurler.devops',
        'url': 'https://www.tiktok.com/@matheusthurler.devops',
        'image': 'images/icons/tiktok.png',
        'external': True,
    },
    {
        'title': 'GitHub',
        'description': 'Meus projetos open source',
        'url': 'https://github.com/Matheus-Thurler',
        'image': 'images/icons/github.png',
        'external': True,
    },
    {
        'title': 'Contato',
        'description': 'contato@matheusthurler.com.br',
        'url': 'mailto:contato@matheusthurler.com.br',
        'image': 'images/icons/email.png',
        'external': True,
    },
]

LINKS_PAGE_EN = [
    {
        'title': 'YouTube Channel',
        'description': 'Videos about DevOps, Kubernetes and Homelab',
        'url': 'https://youtube.com/@matheusthurler',
        'image': 'images/icons/youtube.png',
        'external': True,
    },
    {
        'title': 'Blog',
        'description': 'Technical articles about technology',
        'url_name': 'blog:home',
        'icon': 'posts',
        'external': False,
    },
    {
        'title': 'LinkedIn',
        'description': 'My professional profile',
        'url': 'https://linkedin.com/in/matheus-thurler',
        'image': 'images/icons/linkedin.png',
        'external': True,
    },
    {
        'title': 'Instagram',
        'description': '@maththurler.devops',
        'url': 'https://instagram.com/maththurler.devops',
        'image': 'images/icons/instagram.png',
        'external': True,
    },
    {
        'title': 'TikTok',
        'description': '@matheusthurler.devops',
        'url': 'https://www.tiktok.com/@matheusthurler.devops',
        'image': 'images/icons/tiktok.png',
        'external': True,
    },
    {
        'title': 'GitHub',
        'description': 'My open source projects',
        'url': 'https://github.com/Matheus-Thurler',
        'image': 'images/icons/github.png',
        'external': True,
    },
    {
        'title': 'Contact',
        'description': 'contato@matheusthurler.com.br',
        'url': 'mailto:contato@matheusthurler.com.br',
        'image': 'images/icons/email.png',
        'external': True,
    },
]

# UI Settings (from Hugo theme)
SHOW_THEME_SWITCH = True
SHOW_DARK_MODE_SWITCH = True
SHOW_LANGUAGE_SWITCH = True
SHOW_DOCK = True
STICKY_HEADER = True
LANGUAGE_SWITCH_MODE = 'dropdown'  # or 'cycle'
COLOR_SCHEME = 'nord'
DEFAULT_COLOR_MODE = 'dark'  # dark, light, or system
DOCK_MODE = 'float'  # scroll, always, float

FOOTER_MENU_EN = [
    {'name': 'About', 'url_name': 'blog:about'},
    {'name': 'Contact', 'url': 'mailto:matheus@matheusthurler.com.br', 'external': True},
    {'name': 'RSS Feed', 'url': '/index.xml'},
    {'name': 'Privacy', 'url_name': 'blog:privacy'},
    {'name': 'Terms', 'url_name': 'blog:terms'},
]

FOOTER_MENU_PT = [
    {'name': 'Sobre', 'url_name': 'blog:about'},
    {'name': 'Contato', 'url': 'mailto:matheus@matheusthurler.com.br', 'external': True},
    {'name': 'Feed RSS', 'url': '/index.xml'},
    {'name': 'Privacidade', 'url_name': 'blog:privacy'},
    {'name': 'Termos', 'url_name': 'blog:terms'},
]

# Posts settings
RECENT_POSTS_COUNT = 5
RELATED_POSTS_COUNT = 3

# =============================================================================
# PAGE CACHE (file in prod — shared across gunicorn workers; Redis optional)
# =============================================================================
_default_cache_backend = 'file' if not DEBUG else 'locmem'
CACHE_BACKEND = os.environ.get('CACHE_BACKEND', _default_cache_backend).lower()
CACHE_PAGE_TIMEOUT = int(os.environ.get('CACHE_PAGE_TIMEOUT', '900'))
PUBLIC_CACHE_MAX_AGE = int(os.environ.get('PUBLIC_CACHE_MAX_AGE', '300'))
PUBLIC_CACHE_S_MAXAGE = int(os.environ.get('PUBLIC_CACHE_S_MAXAGE', '3600'))
PRERENDER_OUTPUT_DIR = BASE_DIR.parent / 'hosting' / 'public'

if CACHE_BACKEND == 'redis':
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        }
    }
elif CACHE_BACKEND == 'file':
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': BASE_DIR / 'data' / 'django_cache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'matheus-blog-public',
        }
    }

# Newsletter — Django app replaces content-automation Cloud Function subscribe
NEWSLETTER_SUBSCRIBE_URL = os.environ.get(
    'NEWSLETTER_SUBSCRIBE_URL',
    '',  # empty = use Django /newsletter/subscribe/
)
NEWSLETTER_FROM_EMAIL = os.environ.get('NEWSLETTER_FROM', 'matheus@matheusthurler.com.br')
NEWSLETTER_FROM_NAME = os.environ.get('NEWSLETTER_FROM_NAME', 'Matheus Thurler')
NEWSLETTER_SEND_WELCOME = os.environ.get('NEWSLETTER_SEND_WELCOME', 'True').lower() == 'true'
NEWSLETTER_INTERNAL_TOKEN = (
    os.environ.get('NEWSLETTER_INTERNAL_TOKEN')
    or get_secret('internal-api-token')
)
NEWSLETTER_ALLOWED_ORIGIN = os.environ.get(
    'NEWSLETTER_ALLOWED_ORIGIN',
    'https://matheusthurler.com.br',
)

# Email (console backend in dev; SMTP in production)
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)
EMAIL_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('SMTP_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('NEWSLETTER_FROM', 'matheus@matheusthurler.com.br')
EMAIL_HOST_PASSWORD = os.environ.get('SMTP_PASSWORD') or get_secret('workspace-smtp-password')
DEFAULT_FROM_EMAIL = f'{NEWSLETTER_FROM_NAME} <{NEWSLETTER_FROM_EMAIL}>'

# Comments (Giscus)
COMMENTS_ENABLED = True
GISCUS_REPO = 'Matheus-Thurler/matheus-site-hugo'
GISCUS_REPO_ID = 'R_kgDOQYHuEQ'
GISCUS_CATEGORY = 'Announcements'
GISCUS_CATEGORY_ID = 'DIC_kwDOQYHuEc4Cx73e'
GISCUS_MAPPING = 'pathname'
GISCUS_REACTIONS_ENABLED = True
GISCUS_EMIT_METADATA = False
GISCUS_INPUT_POSITION = 'bottom'
GISCUS_THEME = 'preferred_color_scheme'

# Analytics
ANALYTICS_ENABLED = True
ANALYTICS_SELF_HOSTED = os.environ.get('ANALYTICS_SELF_HOSTED', 'True').lower() == 'true'
GOOGLE_ANALYTICS_ID = 'G-G73F8VFQNC'

# Google AdSense
GOOGLE_ADSENSE_ID = 'pub-3348120452456400'
GOOGLE_ADSENSE_CLIENT_ID = 'ca-pub-3348120452456400'
GOOGLE_ADSENSE_SLOT = 'auto'  # in-article fluid (same as Hugo)

# Code highlighting
CODEBLOCK_COLLAPSE_ENABLED = True
CODEBLOCK_COLLAPSE_DEFAULT = 'expanded'
CODEBLOCK_AUTO_COLLAPSE_LINES = 30
CODEBLOCK_AUTO_COLLAPSE_HEIGHT = 400
CODEBLOCK_COLLAPSED_HEIGHT = 120

# Reading progress
READING_PROGRESS_ENABLED = True
READING_PROGRESS_HEIGHT = 3

# Markdown settings
MARKDOWN_EXTENSIONS = [
    'markdown.extensions.extra',
    'markdown.extensions.toc',
    'markdown.extensions.tables',
    'markdown.extensions.fenced_code',
]

# Pagination
POSTS_PER_PAGE = 6

# Gemini — AI post drafts (admin); falls back to GCP secret gemini-api-key
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or get_secret('gemini-api-key')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-3.5-flash')
# Modelo barato/alto volume (curadoria em lote, etc.)
GEMINI_MODEL_LITE = os.environ.get('GEMINI_MODEL_LITE', 'gemini-3.1-flash-lite')
GEMINI_MODEL_FALLBACKS = [
    m.strip()
    for m in os.environ.get(
        'GEMINI_MODEL_FALLBACKS',
        'gemini-3.6-flash,gemini-3.1-flash-lite,gemini-flash-latest',
    ).split(',')
    if m.strip()
]

# Curation / Discord (content-automation migration)
# Bot token: GCP secret discord-bot-token (same as Cloud Functions)
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN') or get_secret('discord-bot-token')
DISCORD_PUBLIC_KEY = os.environ.get('DISCORD_PUBLIC_KEY') or get_secret('discord-public-key')
DISCORD_DRAFTS_CHANNEL_ID = os.environ.get(
    'DISCORD_DRAFTS_CHANNEL_ID', '1509195028294275203',
)
DISCORD_NEWSLETTER_CHANNEL_ID = os.environ.get(
    'DISCORD_NEWSLETTER_CHANNEL_ID', '1509194617038438574',
)
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')
YOUTUBE_CHANNEL_ID = os.environ.get('YOUTUBE_CHANNEL_ID', 'UCHVZvp_RfNpwfATmQ-NaDyw')
GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME', 'Matheus-Thurler')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
START_HERE_POST_SLUGS = [
    slug.strip()
    for slug in os.environ.get(
        'START_HERE_POST_SLUGS',
        'distrobox-end-of-works-on-my-machine,cloudstack-ansible-video-tutorial,nginx-gateway-api-kubernetes',
    ).split(',')
    if slug.strip()
]
HOMELAB_STATUS_CHECKS = json.loads(os.environ.get('HOMELAB_STATUS_CHECKS', '[]'))
CHANGELOG_PATH = BASE_DIR.parent / 'CHANGELOG.md'
BLOG_RSS_URL = os.environ.get('BLOG_RSS_URL', 'https://matheusthurler.com.br/index.xml')
INTERNAL_API_TOKEN = (
    os.environ.get('INTERNAL_API_TOKEN')
    or get_secret('internal-api-token')
)
GCP_PROJECT = os.environ.get('GCP_PROJECT', 'matheus-cloud-pessoal')

# Jazzmin settings
JAZZMIN_SETTINGS = {
    "site_title": "Matheus Thurler",
    "site_header": "Plataforma MT",
    "site_brand": "MT Platform",
    "welcome_sign": "Painel da plataforma — use o menu lateral ou os atalhos abaixo.",
    "show_sidebar": True,
    "navigation_expanded": False,
    "search_model": ["blog.post"],
    "hide_apps": ["axes", "sites", "socialaccount", "discord_bot"],
    "hide_models": [
        "auth.group",
        "blog.postfeedback",
    ],
    "order_with_respect_to": [
        "blog",
        "pages",
        "media_library",
        "newsletter",
        "campaigns",
        "curation",
        "content_pipeline",
        "integrations",
        "analytics",
        "contact",
        "redirects",
        "auth",
        "blog.post",
        "Gerar post com IA",
        "blog.series",
        "blog.category",
        "blog.tag",
        "blog.author",
        "blog.profilelink",
        "blog.comment",
        "pages.page",
        "media_library.mediaasset",
        "newsletter.subscriber",
        "newsletter.leadmagnet",
        "curation.feedsource",
        "curation.curateditem",
        "curation.linksubmission",
        "campaigns.newslettercampaign",
        "content_pipeline.instagramcarousel",
        "content_pipeline.pipelinejob",
        "integrations.integrationconfig",
        "Dashboard analytics",
        "analytics.pageview",
        "contact.contactmessage",
        "redirects.redirect",
        "auth.user",
    ],
    "icons": {
        "blog": "fas fa-newspaper",
        "blog.post": "fas fa-file-alt",
        "blog.series": "fas fa-layer-group",
        "newsletter": "fas fa-envelope",
        "curation": "fas fa-rss",
        "campaigns": "fas fa-paper-plane",
        "content_pipeline": "fas fa-gears",
        "content_pipeline.instagramcarousel": "fab fa-instagram",
        "pages": "fas fa-file-alt",
        "media_library": "fas fa-images",
        "contact": "fas fa-inbox",
        "analytics": "fas fa-chart-line",
        "redirects": "fas fa-route",
        "integrations": "fas fa-plug",
        "auth": "fas fa-users-cog",
    },
    "custom_links": {
        "blog": [{
            "name": "Gerar post com IA",
            "url": "admin:blog_post_generate_ai",
            "icon": "fas fa-wand-magic-sparkles",
            "permissions": ["blog.add_post"],
        }],
        "analytics": [{
            "name": "Dashboard analytics",
            "url": "/admin/analytics/pageview/dashboard/",
            "icon": "fas fa-chart-pie",
        }],
        "content_pipeline": [{
            "name": "Carrosséis Instagram",
            "url": "/admin/content_pipeline/instagramcarousel/",
            "icon": "fab fa-instagram",
        }],
    },
    "topnav_links": [
        {"name": "Ver Site", "url": "/", "icon": "fa-globe"},
        {"name": "GitHub", "url": "https://github.com/Matheus-Thurler", "icon": "fa-github"},
    ],
    "custom_css": "css/admin.css",
    "custom_js": "js/admin-sidebar.js",
}

JAZZMIN_UI_TWEAKS = {
    "sidebar_fixed": True,
    "navbar_fixed": True,
    "sidebar_nav_compact_style": True,
}

# =============================================================================
# SECURITY HARDENING
# =============================================================================

# Core Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'

# SSL/HTTPS Settings (applied when DEBUG=False)
if not DEBUG:
    # Force HTTPS redirects
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Secure cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    WHITENOISE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days — Lighthouse cache lifetime

    # Firebase Hosting → Cloud Run rewrites strip every cookie except __session.
    # Without this, admin login succeeds then immediately returns to the login page.
    SESSION_COOKIE_NAME = '__session'
    CSRF_USE_SESSIONS = True  # csrftoken cookie is also stripped by Firebase CDN

    # Cloud Run / Docker health probes hit /health/ with Host: 127.0.0.1
    for _probe_host in ('127.0.0.1', 'localhost'):
        if _probe_host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(_probe_host)
else:
    # Development settings
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = None

    # Cache headers for static files (production reverse proxy config)
    # Add these headers in nginx/apache for production:
    # nginx: expires 30d; add_header Cache-Control "public, immutable";
    STATICFILES_AUTO_PREFIX = True

# Session Security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF Security
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# =============================================================================
# DJANGO-AXES: Brute Force Protection
# =============================================================================
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5  # Number of failed attempts before lockout
AXES_COOLOFF_TIME = 1  # 1 hour lockout after failed attempts
AXES_LOCK_OUT_AT_FAILURE = True
# Firebase Hosting → Cloud Run: client IP is not reliable (often 169.254.x.x).
# Lock by username only to avoid shared-IP false lockouts.
AXES_LOCKOUT_PARAMETERS = ['username']
AXES_RESET_ON_SUCCESS = True  # Reset failure count on successful login

# =============================================================================
# DJANGO-CSP: Content Security Policy (v4.0+ format)
# =============================================================================
# Default CSP: allow 'self' for all
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'",),
        'script-src': (
            "'self'",
            "'unsafe-inline'",
            'blob:',
            'https://www.googletagmanager.com',
            'https://pagead2.googlesyndication.com',
            'https://googleads.g.doubleclick.net',
            'https://www.google.com',
            'https://giscus.app',
            'https://cdn.jsdelivr.net',
            'https://asciinema.org',
        ),
        'style-src': ("'self'", "'unsafe-inline'"),
        'img-src': (
            "'self'",
            'https://pagead2.googlesyndication.com',
            'https://googleads.g.doubleclick.net',
            'https://www.google.com',
            'https://www.gstatic.com',
            'https://img.youtube.com',
            'https://i.ytimg.com',
            'https://avatars.githubusercontent.com',
            'https://*.githubusercontent.com',
            'https://media-site-matheus-nuxt.s3.amazonaws.com',
            'data:',
            'blob:',
        ),
        'frame-src': (
            "'self'",
            'https://www.youtube.com',
            'https://img.youtube.com',
            'https://giscus.app',
            'https://googleads.g.doubleclick.net',
            'https://tpc.googlesyndication.com',
            'https://www.google.com',
            'https://asciinema.org',
        ),
        'connect-src': (
            "'self'",
            'https://api.github.com',
            'https://giscus.app',
            'https://*.githubusercontent.com',
            'https://accounts.google.com',
            'https://www.google-analytics.com',
            'https://*.google-analytics.com',
            'https://www.googletagmanager.com',
            'https://pagead2.googlesyndication.com',
            'https://googleads.g.doubleclick.net',
            'https://ep1.adtrafficquality.google',
        ),
        'font-src': ("'self'", 'https://fonts.gstatic.com'),
        'worker-src': ("'self'", 'blob:'),
        'media-src': ("'self'", 'https://img.youtube.com', 'https://i.ytimg.com'),
        'object-src': ("'none'",),
        'base-uri': ("'self'",),
        'form-action': ("'self'",),
        'frame-ancestors': ("'none'",),
    }
}

# Upgrade insecure requests in production
if not DEBUG:
    CONTENT_SECURITY_POLICY['DIRECTIVES']['upgrade-insecure-requests'] = True
# CSP_REPORT_ONLY = False

# =============================================================================
# DJANGO-RATELIMIT: Rate Limiting
# =============================================================================
# Ratelimit settings are configured per-view in views.py
# Default rates for anonymous users
RATELIMIT_DEFAULT_RATE = '100/day'
RATELIMIT_HEADERS_ENABLED = True

# =============================================================================
# XSS PROTECTION: Bleach for Markdown
# =============================================================================
# Allowed HTML tags in markdown (security hardening)
BLEACH_ALLOWED_TAGS = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'br', 'hr',
    'ul', 'ol', 'li',
    'blockquote', 'pre', 'code',
    'a', 'strong', 'em', 'del', 's',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'img', 'div', 'span', 'button', 'svg', 'path',
]

BLEACH_ALLOWED_ATTRIBUTES = {
    '*': ['class', 'id', 'title', 'aria-hidden', 'aria-label', 'type', 'data-code-id',
          'data-default-state', 'data-collapsed', 'data-auto-collapse-lines',
          'data-auto-collapse-height', 'data-collapsed-height', 'data-collapse-init'],
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'title', 'class', 'loading'],
    'code': ['class'],
    'pre': ['class'],
    'div': ['class', 'id'],
    'span': ['class'],
    'button': ['class', 'type', 'title', 'aria-label', 'data-code-id', 'data-default-state',
               'data-collapsed', 'data-auto-collapse-lines', 'data-auto-collapse-height',
               'data-collapsed-height', 'data-collapse-init'],
    'svg': ['class', 'fill', 'stroke', 'viewBox', 'aria-hidden', 'xmlns', 'width', 'height'],
    'path': ['d', 'stroke-linecap', 'stroke-linejoin', 'stroke-width', 'fill'],
    'th': ['align'],
    'td': ['align', 'class'],
    'tr': ['class'],
}

BLEACH_ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']
BLEACH_STRIP_TAGS = True
BLEACH_STRIP_COMMENTS = True
