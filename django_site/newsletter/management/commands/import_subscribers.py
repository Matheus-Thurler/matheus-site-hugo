"""Import subscribers from content-automation GCS subscribers.json format."""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime

from newsletter.models import Subscriber


class Command(BaseCommand):
    help = 'Import subscribers from subscribers.json (content-automation format)'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='Path to subscribers.json')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without saving',
        )

    def handle(self, *args, **options):
        path = Path(options['file'])
        if not path.exists():
            self.stderr.write(self.style.ERROR(f'File not found: {path}'))
            return

        data = json.loads(path.read_text(encoding='utf-8'))
        subscribers = data.get('subscribers', [])

        created = 0
        updated = 0
        skipped = 0

        for entry in subscribers:
            email = entry.get('email', '').strip()
            name = entry.get('name', '').strip()
            if not email or not name:
                skipped += 1
                continue

            subscribed_at = parse_datetime(entry.get('subscribed_at', ''))
            language = entry.get('language', 'en')
            if language not in ('en', 'pt'):
                language = 'en'

            defaults = {
                'name': name,
                'language': language,
                'is_active': True,
            }
            if subscribed_at:
                defaults['subscribed_at'] = subscribed_at

            if options['dry_run']:
                exists = Subscriber.objects.filter(email__iexact=email).exists()
                action = 'update' if exists else 'create'
                self.stdout.write(f'  [{action}] {email} ({name})')
                continue

            obj, was_created = Subscriber.objects.update_or_create(
                email=email,
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        if options['dry_run']:
            self.stdout.write(self.style.WARNING(f'Dry run: {len(subscribers)} entries processed'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Import complete: {created} created, {updated} updated, {skipped} skipped'
            ))
