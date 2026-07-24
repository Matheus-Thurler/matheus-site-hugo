from django.core.management.base import BaseCommand

from content_pipeline.services import run_pipeline


class Command(BaseCommand):
    help = 'Run editorial pipeline (curation, newsletter draft, sync)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type', choices=['full', 'curation', 'newsletter', 'sync'], default='full',
        )
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        job = run_pipeline(job_type=options['type'], dry_run=options['dry_run'])
        style = self.style.SUCCESS if job.status == 'success' else self.style.ERROR
        self.stdout.write(style(f'Pipeline {job.pk}: {job.status}'))
        if job.log:
            self.stdout.write(job.log)
