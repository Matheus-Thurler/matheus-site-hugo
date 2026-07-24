from django.core.management.base import BaseCommand

from integrations.services import sync_all


class Command(BaseCommand):
    help = 'Sync YouTube and GitHub integrations'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        results = sync_all(dry_run=options['dry_run'])
        self.stdout.write(str(results))
