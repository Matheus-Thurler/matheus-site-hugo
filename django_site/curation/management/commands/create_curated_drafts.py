from django.core.management.base import BaseCommand

from curation.services import create_drafts_from_approved


class Command(BaseCommand):
    help = 'Create blog Post drafts from approved curated items'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=None)

    def handle(self, *args, **options):
        created = create_drafts_from_approved(limit=options['limit'])
        self.stdout.write(self.style.SUCCESS(f'Created {created} draft(s)'))
