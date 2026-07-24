"""Views for blog app."""
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.utils.translation import get_language
from django.core.paginator import Paginator
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
from .models import Post, Category, Tag, Author, Comment
from .forms import CommentForm
from .markdown_utils import render_markdown, plain_text


def get_current_language():
    """Get current language code."""
    lang = get_language()
    return lang if lang in ['en', 'pt'] else 'en'


class CategoriesView(TemplateView):
    """List all categories."""
    template_name = 'blog/categories.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('name')
        context['lang'] = get_current_language()
        return context


class TagsView(TemplateView):
    """List all tags."""
    template_name = 'blog/tags.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all().order_by('name')
        context['lang'] = get_current_language()
        return context


class PostListView(ListView):
    """List view for published posts."""
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        return Post.objects.published()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lang'] = get_current_language()
        return context


class PostDetailView(DetailView):
    """Detail view for a single post."""
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'

    def get_queryset(self):
        return Post.objects.published()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lang = get_current_language()
        context['lang'] = lang
        context['title'] = self.object.get_title(lang)
        context['description'] = self.object.get_description(lang)
        content_html, table_of_contents = render_markdown(self.object.get_content(lang))
        context['content'] = content_html
        context['table_of_contents'] = table_of_contents
        context['show_reading_progress'] = True
        context['show_toc'] = bool(table_of_contents)

        # Related posts
        if self.object.show_related:
            related = Post.objects.published().filter(
                category=self.object.category
            ).exclude(id=self.object.id)[:settings.RELATED_POSTS_COUNT]
            context['related_posts'] = related

        # Comments
        context['comments'] = self.object.comments.filter(status='approved')
        context['comment_form'] = CommentForm()

        return context


@login_required
@ratelimit(key='user', rate='5/hour', method='POST', block=True)
@ratelimit(key='user', rate='10/day', method='POST', block=True)
@require_http_methods(["POST"])
def add_comment(request, slug):
    """Add a new comment to a post."""
    post = get_object_or_404(Post, slug=slug)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.status = 'pending'  # Requires moderation
            comment.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Comentário enviado para moderação!'})

            messages.success(request, 'Comentário enviado para moderação!')
            return redirect('blog:post_detail', slug=slug)
    else:
        form = CommentForm()

    return redirect('blog:post_detail', slug=slug)


class CategoryListView(ListView):
    """List posts by category."""
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.published().filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['lang'] = get_current_language()
        return context


class TagListView(ListView):
    """List posts by tag."""
    model = Post
    template_name = 'blog/tag.html'
    context_object_name = 'posts'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Post.objects.published().filter(tags=self.tag)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        context['lang'] = get_current_language()
        return context


class ArchivesView(ListView):
    """Archive view - grouped by year/month."""
    model = Post
    template_name = 'blog/archives.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.published()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lang'] = get_current_language()

        # Group by year
        posts_by_year = {}
        for post in context['posts']:
            year = post.published_at.year
            if year not in posts_by_year:
                posts_by_year[year] = []
            posts_by_year[year].append(post)

        context['posts_by_year'] = dict(sorted(posts_by_year.items(), reverse=True))
        return context


def _load_youtube_data():
    path = settings.BASE_DIR / 'data' / 'youtube.json'
    if not path.exists():
        return {}
    with path.open(encoding='utf-8') as handle:
        return json.load(handle)


def home(request):
    """Home page view."""
    lang = get_current_language()
    recent_posts = Post.objects.published()[:settings.RECENT_POSTS_COUNT]

    # Get or create default author
    author, _ = Author.objects.get_or_create(
        slug='matheus-thurler',
        defaults={
            'name': settings.AUTHOR_NAME,
            'title': settings.AUTHOR_TITLE,
            'description': settings.AUTHOR_DESCRIPTION,
            'avatar': 'images/avatar.webp',
            'github': settings.AUTHOR_GITHUB,
            'youtube': settings.AUTHOR_YOUTUBE,
            'linkedin': settings.AUTHOR_LINKEDIN,
            'email': settings.AUTHOR_EMAIL,
        }
    )

    context = {
        'lang': lang,
        'recent_posts': recent_posts,
        'author': author,
        'newsletter_url': settings.NEWSLETTER_SUBSCRIBE_URL or reverse('newsletter:subscribe'),
        'youtube_data': _load_youtube_data(),
        'show_reading_progress': False,
    }
    return render(request, 'blog/home.html', context)


def about(request):
    """About page view."""
    lang = get_current_language()

    # Get or create default author
    author, _ = Author.objects.get_or_create(
        slug='matheus-thurler',
        defaults={
            'name': settings.AUTHOR_NAME,
            'title': settings.AUTHOR_TITLE,
            'description': settings.AUTHOR_DESCRIPTION,
            'content_teaching': settings.AUTHOR_CONTENT_TEACHING,
            'goals': settings.AUTHOR_GOALS,
            'github': settings.AUTHOR_GITHUB,
            'youtube': settings.AUTHOR_YOUTUBE,
            'linkedin': settings.AUTHOR_LINKEDIN,
            'email': settings.AUTHOR_EMAIL,
        }
    )

    # Convert goals text to list
    goals_list = []
    if author.goals:
        goals_list = [g.strip() for g in author.goals.split('\n') if g.strip()]

    context = {
        'lang': lang,
        'author': author,
        'goals_list': goals_list,
    }
    return render(request, 'blog/about.html', context)


def _resolve_links_page(lang):
    """Build links page entries with resolved URLs."""
    from blog.links_page import get_card_links

    return get_card_links(lang)


def _get_social_links():
    from blog.links_page import get_social_links

    return get_social_links()


def links(request):
    """Links page view (link-in-bio layout matching Hugo)."""
    lang = get_current_language()
    from django.conf import settings

    context = {
        'lang': lang,
        'page_title': 'Links',
        'page_description': (
            'Todos os meus links importantes em um só lugar'
            if lang == 'pt'
            else 'All my important links in one place'
        ),
        'page_links': _resolve_links_page(lang),
        'author_avatar': settings.AUTHOR_AVATAR,
        'author_links_subtitle': settings.AUTHOR_LINKS_SUBTITLE,
        'author_social': _get_social_links(),
    }
    return render(request, 'blog/links.html', context)


def privacy(request):
    """Privacy policy page view."""
    lang = get_current_language()
    return render(request, 'blog/privacy.html', {'lang': lang})


def terms(request):
    """Terms of service page view."""
    lang = get_current_language()
    return render(request, 'blog/terms.html', {'lang': lang})


def search(request):
    """Search posts view."""
    query = request.GET.get('q', '')
    lang = get_current_language()

    if query:
        posts = Post.objects.published().filter(
            title_en__icontains=query
        ) | Post.objects.published().filter(
            title_pt__icontains=query
        )
    else:
        posts = Post.objects.none()

    context = {
        'lang': lang,
        'query': query,
        'posts': posts,
        'show_reading_progress': True,
    }
    return render(request, 'blog/search.html', context)


def search_index(request):
    """JSON search index compatible with Hugo search.js."""
    lang = get_current_language()
    posts = []
    for post in Post.objects.published():
        posts.append({
            'title': post.get_title(lang),
            'text': plain_text(post.get_content(lang), max_length=2000),
            'link': post.get_absolute_url(),
        })

    tags = [
        {'name': tag.name, 'slug': tag.slug, 'link': tag.get_absolute_url()}
        for tag in Tag.objects.all()
    ]
    categories = [
        {'name': category.name, 'slug': category.slug, 'link': category.get_absolute_url()}
        for category in Category.objects.all()
    ]

    return JsonResponse({
        'posts': posts,
        'pages': [],
        'tags': tags,
        'categories': categories,
    })


def robots_txt(request):
    """robots.txt with absolute Sitemap URL (Lighthouse SEO requirement)."""
    sitemap_url = request.build_absolute_uri('/sitemap.xml')
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        'Disallow: /accounts/',
        'Disallow: /i18n/',
        '',
        f'Sitemap: {sitemap_url}',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


def health_check(request):
    """Lightweight liveness probe for Cloud Run deploy smoke tests."""
    return JsonResponse({'status': 'ok'})
