from django.core.management.base import BaseCommand

from curation.services import run_curation


class Command(BaseCommand):
    help = 'Fetch RSS feeds, summarize with Gemini, notify Discord'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        n = run_curation(dry_run=options['dry_run'])
        self.stdout.write(self.style.SUCCESS(f'Curation done: {n} new items'))
