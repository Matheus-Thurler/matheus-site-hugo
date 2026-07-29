"""Prerender public HTML for Firebase Hosting CDN (SSG-like)."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.test import Client

from blog.models import Category, Post, Tag

# Pages with forms or dynamic query strings — not useful as static snapshots.
_SKIP_PATHS = frozenset({'/search/', '/pt/search/'})


class Command(BaseCommand):
    help = 'Prerender public pages to hosting/public for Firebase CDN static serving.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--base-url',
            help='Fetch pages from a running server (Cloud Run URL in CI).',
        )
        parser.add_argument(
            '--output',
            default='',
            help='Output directory (default: repo hosting/public).',
        )
        parser.add_argument(
            '--host',
            default='',
            help='Canonical Host header (default: SITE_CANONICAL_HOST).',
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            default=True,
            help='Remove previous prerender output before writing (default: true).',
        )
        parser.add_argument(
            '--no-clean',
            action='store_false',
            dest='clean',
            help='Keep existing prerender files.',
        )

    def handle(self, *args, **options):
        output_dir = Path(options['output'] or settings.PRERENDER_OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)

        canonical_host = options['host'] or settings.SITE_CANONICAL_HOST
        paths = self._collect_paths()
        base_url = (options.get('base_url') or '').rstrip('/')

        if options['clean']:
            self._clean_output_dir(output_dir)

        if base_url:
            written = self._fetch_from_server(
                base_url, paths, output_dir, canonical_host,
            )
        else:
            written = self._render_with_client(paths, output_dir, canonical_host)

        self.stdout.write(self.style.SUCCESS(
            f'Prerendered {written} pages → {output_dir} (host={canonical_host})',
        ))

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
            '/pt/',
            '/pt/posts/',
            '/pt/categories/',
            '/pt/tags/',
            '/pt/archives/',
            '/pt/about/',
            '/pt/links/',
            '/pt/privacy/',
            '/pt/terms/',
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

        return [p for p in paths if p not in _SKIP_PATHS]

    def _client_kwargs(self, host: str) -> dict[str, str]:
        return {
            'HTTP_HOST': host,
            'HTTP_X_FORWARDED_PROTO': 'https',
            'HTTP_X_FORWARDED_HOST': host,
        }

    def _render_with_client(self, paths: list[str], output_dir: Path, host: str) -> int:
        client = Client(**self._client_kwargs(host))
        written = 0
        for path in paths:
            response = client.get(path)
            if response.status_code != 200:
                self.stdout.write(self.style.WARNING(f'Skip {path} ({response.status_code})'))
                continue
            body = self._normalize_html(response.content, host)
            self._write_html(output_dir, path, body)
            written += 1
        return written

    def _fetch_from_server(
        self,
        base_url: str,
        paths: list[str],
        output_dir: Path,
        canonical_host: str,
    ) -> int:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'matheus-blog-prerender/1.0',
            'Host': canonical_host,
            'X-Forwarded-Proto': 'https',
            'X-Forwarded-Host': canonical_host,
        })
        fetched_host = urlparse(base_url).netloc
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
            body = self._normalize_html(response.content, fetched_host, canonical_host)
            self._write_html(output_dir, path, body)
            written += 1
        return written

    def _normalize_html(
        self,
        content: bytes,
        *hosts_to_replace: str,
    ) -> bytes:
        """Rewrite absolute URLs to the canonical production domain."""
        canonical = settings.SITE_CANONICAL_URL
        text = content.decode('utf-8')
        for host in hosts_to_replace:
            if not host:
                continue
            text = text.replace(f'https://{host}', canonical)
            text = text.replace(f'http://{host}', canonical)
        # Cloud Run regional URLs (*.run.app)
        text = re.sub(
            r'https://[a-z0-9-]+(?:\.[a-z0-9-]+)*\.run\.app',
            canonical,
            text,
        )
        text = re.sub(
            r'http://[a-z0-9-]+(?:\.[a-z0-9-]+)*\.run\.app',
            canonical,
            text,
        )
        return text.encode('utf-8')

    def _write_html(self, output_dir: Path, path: str, content: bytes) -> None:
        normalized = path if path.endswith('/') else f'{path}/'
        rel = normalized.lstrip('/')
        target = output_dir / rel / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    def _clean_output_dir(self, output_dir: Path) -> None:
        for item in output_dir.iterdir():
            if item.name == '.gitkeep':
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
