from django.core.management.base import BaseCommand

from content_pipeline.scheduler import JOBS, run_job


class Command(BaseCommand):
    help = 'Run scheduled jobs (check_content daily, curate weekly)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--job',
            choices=list(JOBS.keys()),
            default='full',
            help='Job to run (default: full)',
        )
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        job_name = options['job']
        if options['dry_run']:
            self.stdout.write(self.style.WARNING(f'DRY RUN: {job_name}'))
        job = run_job(job_name, dry_run=options['dry_run'])
        style = self.style.SUCCESS if job.status == 'success' else self.style.ERROR
        self.stdout.write(style(f'Job {job.pk}: {job.status}'))
        if job.log:
            self.stdout.write(job.log)
