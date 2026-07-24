"""Update existing posts to have proper EN/PT content from Hugo."""
import os
import re
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from blog.models import Author, Category, Tag, Post


class Command(BaseCommand):
    help = 'Update existing posts with proper EN/PT content from Hugo files'

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

        author, _ = Author.objects.get_or_create(
            slug='matheus-thurler',
            defaults={
                'name': settings.AUTHOR_NAME,
                'title': settings.AUTHOR_TITLE,
                'description': settings.AUTHOR_DESCRIPTION,
            }
        )

        updated = 0
        en_files = {}
        pt_files = {}

        # Group files by language
        for filename in os.listdir(hugo_dir):
            if not filename.endswith('.md'):
                continue

            is_portuguese = filename.endswith('.pt.md')
            slug = filename.replace('.pt.md', '').replace('.md', '')

            filepath = os.path.join(hugo_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            frontmatter, body = self.parse_frontmatter(content)

            post_data = {
                'title': frontmatter.get('title', ''),
                'description': frontmatter.get('description', ''),
                'content': body.strip(),
                'date': frontmatter.get('date', ''),
                'categories': frontmatter.get('categories', []),
                'tags': frontmatter.get('tags', []),
                'draft': frontmatter.get('draft', 'false').lower() == 'true',
                'cover': frontmatter.get('cover', ''),
            }

            if is_portuguese:
                pt_files[slug] = post_data
            else:
                en_files[slug] = post_data

        # Update posts with both EN and PT content
        for slug in set(list(en_files.keys()) + list(pt_files.keys())):
            try:
                post = Post.objects.get(slug=slug)
            except Post.DoesNotExist:
                self.stdout.write(f'Not found: {slug}')
                continue

            updated_this = False

            if slug in en_files:
                data = en_files[slug]
                if data['title']:
                    post.title_en = data['title']
                    updated_this = True
                if data['description']:
                    post.description_en = data['description']
                    updated_this = True
                if data['content']:
                    post.content_en = data['content']
                    updated_this = True

            if slug in pt_files:
                data = pt_files[slug]
                if data['title']:
                    post.title_pt = data['title']
                    updated_this = True
                if data['description']:
                    post.description_pt = data['description']
                    updated_this = True
                if data['content']:
                    post.content_pt = data['content']
                    updated_this = True

            # Use whichever file has date
            date_data = en_files.get(slug) or pt_files.get(slug)
            if date_data and date_data['date']:
                try:
                    post.published_at = datetime.fromisoformat(
                        date_data['date'].replace('Z', '+00:00')
                    )
                    updated_this = True
                except ValueError:
                    pass

            # Set status from draft flag
            is_draft = date_data and date_data.get('draft', False)
            new_status = 'draft' if is_draft else 'published'
            if post.status != new_status:
                post.status = new_status
                updated_this = True

            # Update category
            cat_data = en_files.get(slug) or pt_files.get(slug)
            if cat_data and cat_data['categories']:
                cat_name = cat_data['categories'][0] if isinstance(cat_data['categories'], list) else cat_data['categories']
                category, _ = Category.objects.get_or_create(
                    slug=cat_name.lower().replace(' ', '-'),
                    defaults={'name': cat_name}
                )
                post.category = category
                updated_this = True

            # Update tags
            tag_data = en_files.get(slug) or pt_files.get(slug)
            if tag_data and tag_data['tags']:
                tag_objects = []
                for tag_name in tag_data['tags'] if isinstance(tag_data['tags'], list) else [tag_data['tags']]:
                    tag, _ = Tag.objects.get_or_create(
                        slug=tag_name.lower().replace(' ', '-'),
                        defaults={'name': tag_name}
                    )
                    tag_objects.append(tag)
                post.tags.set(tag_objects)
                updated_this = True

            # Sync cover from Hugo frontmatter
            cover_data = en_files.get(slug) or pt_files.get(slug)
            if cover_data and cover_data.get('cover') and post.cover != cover_data['cover']:
                post.cover = cover_data['cover']
                updated_this = True

            if updated_this:
                post.save()
                updated += 1
                self.stdout.write(f'Updated: {slug} (EN: {bool(post.title_en)}, PT: {bool(post.title_pt)})')

        self.stdout.write(self.style.SUCCESS(f'\nDone! Updated: {updated}'))

    def parse_frontmatter(self, content):
        """Parse Hugo frontmatter."""
        pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(pattern, content, re.DOTALL)

        if not match:
            return {}, content

        frontmatter_text = match.group(1)
        body = match.group(2)

        data = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                if value.startswith('[') and value.endswith(']'):
                    value = [v.strip().strip('"\'') for v in value[1:-1].split(',')]
                data[key] = value

        return data, body
