"""Import posts from Hugo content directory."""
import os
import re
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from blog.models import Author, Category, Tag, Post


class Command(BaseCommand):
    help = 'Import posts from Hugo content directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hugo-dir',
            type=str,
            default=str(settings.BASE_DIR / 'content' / 'posts'),
            help='Path to Hugo posts directory'
        )

    def handle(self, *args, **options):
        hugo_dir = options['hugo_dir']

        if not os.path.exists(hugo_dir):
            self.stderr.write(f'Directory not found: {hugo_dir}')
            return

        # Create default author
        author, _ = Author.objects.get_or_create(
            slug='matheus-thurler',
            defaults={
                'name': settings.AUTHOR_NAME,
                'title': settings.AUTHOR_TITLE,
                'description': settings.AUTHOR_DESCRIPTION,
            }
        )
        self.stdout.write(f'Author: {author.name}')

        imported = 0
        skipped = 0

        for filename in os.listdir(hugo_dir):
            if not filename.endswith('.md'):
                continue

            filepath = os.path.join(hugo_dir, filename)

            # Determine language from filename
            is_portuguese = filename.endswith('.pt.md')
            slug = filename.replace('.pt.md', '').replace('.md', '')

            # Check if post already exists
            if Post.objects.filter(slug=slug).exists():
                skipped += 1
                self.stdout.write(f'Skipped (exists): {slug}')
                continue

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse frontmatter
            frontmatter, body = self.parse_frontmatter(content)

            # Extract fields
            title = frontmatter.get('title', '')
            description = frontmatter.get('description', '')
            date_str = frontmatter.get('date', '')
            categories = frontmatter.get('categories', [])
            tags = frontmatter.get('tags', [])
            keywords = frontmatter.get('keywords', '')
            cover = frontmatter.get('cover', '')

            # Parse date
            published_at = None
            if date_str:
                try:
                    published_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except ValueError:
                    pass

            # Assign to English or Portuguese fields
            if is_portuguese:
                title_pt = title
                description_pt = description
                content_pt = body.strip()
                title_en = ''
                description_en = ''
                content_en = ''
            else:
                title_en = title
                description_en = description
                content_en = body.strip()
                title_pt = ''
                description_pt = ''
                content_pt = ''

            # Create category
            category = None
            if categories:
                cat_name = categories[0] if isinstance(categories, list) else categories
                category, _ = Category.objects.get_or_create(
                    slug=cat_name.lower().replace(' ', '-'),
                    defaults={'name': cat_name}
                )

            # Create tags
            tag_objects = []
            if tags:
                for tag_name in tags if isinstance(tags, list) else [tags]:
                    tag, _ = Tag.objects.get_or_create(
                        slug=tag_name.lower().replace(' ', '-'),
                        defaults={'name': tag_name}
                    )
                    tag_objects.append(tag)

            # Create post
            post = Post.objects.create(
                author=author,
                category=category,
                slug=slug,
                status='published',
                title_en=title_en,
                description_en=description_en,
                content_en=content_en,
                title_pt=title_pt,
                description_pt=description_pt,
                content_pt=content_pt,
                published_at=published_at,
                keywords=keywords,
                cover=cover,
            )

            if tag_objects:
                post.tags.set(tag_objects)

            imported += 1
            self.stdout.write(f'Imported: {slug}')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Imported: {imported}, Skipped: {skipped}'
        ))

    def parse_frontmatter(self, content):
        """Parse Hugo frontmatter."""
        pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(pattern, content, re.DOTALL)

        if not match:
            return {}, content

        frontmatter_text = match.group(1)
        body = match.group(2)

        # Simple YAML-like parsing
        data = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                if value.startswith('[') and value.endswith(']'):
                    # List
                    value = [v.strip().strip('"\'') for v in value[1:-1].split(',')]
                data[key] = value

        return data, body
