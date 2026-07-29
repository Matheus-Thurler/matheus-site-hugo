"""Prerender public HTML for Firebase Hosting CDN (SSG-like)."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.test import Client

from blog.models import Category, Post, Tag


class Command(BaseCommand):
    help = 'Prerender public pages to hosting/public for Firebase CDN static serving.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--base-url',
            help='Fetch pages from a running server (e.g. Cloud Run candidate URL).',
        )
        parser.add_argument(
            '--output',
            default='',
            help='Output directory (default: repo hosting/public).',
        )
        parser.add_argument(
            '--host',
            default='localhost',
            help='HTTP Host header when rendering via Django test client.',
        )

    def handle(self, *args, **options):
        output_dir = Path(options['output'] or settings.PRERENDER_OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = self._collect_paths()
        base_url = (options.get('base_url') or '').rstrip('/')

        if base_url:
            written = self._fetch_from_server(base_url, paths, output_dir)
        else:
            written = self._render_with_client(paths, output_dir, options['host'])

        self.stdout.write(self.style.SUCCESS(f'Prerendered {written} pages → {output_dir}'))

    def _collect_paths(self) -> list[str]:
        paths = [
            '/',
            '/posts/',
            '/categories/',
            '/tags/',
            '/archives/',
            '/about/',
            '/links/',
            '/privacy/',
            '/terms/',
            '/search/',
            '/pt/',
            '/pt/posts/',
            '/pt/categories/',
            '/pt/tags/',
            '/pt/archives/',
            '/pt/about/',
            '/pt/links/',
            '/pt/privacy/',
            '/pt/terms/',
            '/pt/search/',
        ]

        for post in Post.objects.published().values_list('slug', flat=True):
            paths.append(f'/posts/{post}/')
            paths.append(f'/pt/posts/{post}/')

        for slug in Category.objects.values_list('slug', flat=True):
            paths.append(f'/categories/{slug}/')
            paths.append(f'/pt/categories/{slug}/')

        for slug in Tag.objects.values_list('slug', flat=True):
            paths.append(f'/tags/{slug}/')
            paths.append(f'/pt/tags/{slug}/')

        return paths

    def _render_with_client(self, paths: list[str], output_dir: Path, host: str) -> int:
        client = Client(HTTP_HOST=host)
        written = 0
        for path in paths:
            response = client.get(path)
            if response.status_code != 200:
                self.stdout.write(self.style.WARNING(f'Skip {path} ({response.status_code})'))
                continue
            self._write_html(output_dir, path, response.content)
            written += 1
        return written

    def _fetch_from_server(self, base_url: str, paths: list[str], output_dir: Path) -> int:
        session = requests.Session()
        session.headers.update({'User-Agent': 'matheus-blog-prerender/1.0'})
        written = 0
        for path in paths:
            url = urljoin(base_url + '/', path.lstrip('/'))
            try:
                response = session.get(url, timeout=30)
            except requests.RequestException as exc:
                self.stdout.write(self.style.WARNING(f'Skip {path}: {exc}'))
                continue
            if response.status_code != 200:
                self.stdout.write(self.style.WARNING(f'Skip {path} ({response.status_code})'))
                continue
            self._write_html(output_dir, path, response.content)
            written += 1
        return written

    def _write_html(self, output_dir: Path, path: str, content: bytes) -> None:
        normalized = path if path.endswith('/') else f'{path}/'
        rel = normalized.lstrip('/')
        target = output_dir / rel / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
