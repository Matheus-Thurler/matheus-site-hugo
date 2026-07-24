"""Scheduled jobs — replaces Cloud Scheduler + Pub/Sub triggers."""
import logging

logger = logging.getLogger(__name__)

JOBS = {
    'check_content': 'Daily check for new blog/video content',
    'curate': 'Weekly newsletter curation + Discord review',
    'full': 'Run daily check + weekly curation',
}


def run_job(job_name: str, *, dry_run=False):
    from content_pipeline.models import PipelineJob
    from django.utils import timezone

    job_type_map = {'check_content': 'sync', 'curate': 'curation', 'full': 'full'}
    job = PipelineJob.objects.create(
        job_type=job_type_map.get(job_name, 'full'),
        status='running',
        started_at=timezone.now(),
    )
    try:
        if job_name in ('check_content', 'full'):
            from curation.weekly import run_daily_content_check

            items = run_daily_content_check(post_to_discord=not dry_run)
            job.append_log(f'Daily check: {len(items)} new items')

        if job_name in ('curate', 'full'):
            from curation.weekly import run_weekly_curation

            campaign = run_weekly_curation(post_to_discord=not dry_run)
            job.append_log(f'Weekly curation: campaign #{campaign.pk}')

        job.status = 'success'
    except Exception as exc:
        logger.exception('Scheduled job %s failed', job_name)
        job.append_log(f'ERROR: {exc}')
        job.status = 'failed'
    finally:
        job.finished_at = timezone.now()
        job.save(update_fields=['status', 'finished_at'])
    return job
