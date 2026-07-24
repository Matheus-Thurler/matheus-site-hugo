"""Run editorial pipeline steps."""
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


def run_pipeline(job_type='full', dry_run=False):
    from .models import PipelineJob

    job = PipelineJob.objects.create(job_type=job_type, status='running', started_at=timezone.now())
    try:
        if job_type in ('full', 'curation'):
            from curation.services import run_curation
            n = run_curation(dry_run=dry_run)
            job.append_log(f'Curation: {n} new items')

        if job_type in ('full', 'newsletter'):
            from campaigns.services import build_weekly_campaign
            campaign = build_weekly_campaign()
            job.append_log(f'Newsletter draft #{campaign.pk} created')

        if job_type in ('full', 'sync'):
            from integrations.services import sync_all
            results = sync_all(dry_run=dry_run)
            job.append_log(f'Sync: {results}')

        job.status = 'success'
    except Exception as exc:
        logger.exception('Pipeline failed')
        job.append_log(f'ERROR: {exc}')
        job.status = 'failed'
    finally:
        job.finished_at = timezone.now()
        job.save(update_fields=['status', 'finished_at'])
    return job
