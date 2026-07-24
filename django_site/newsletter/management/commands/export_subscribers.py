"""Export subscribers to content-automation GCS subscribers.json format."""
import json
from pathlib import Path

from django.core.management.base import BaseCommand

from newsletter.models import Subscriber


class Command(BaseCommand):
    help = 'Export active subscribers to subscribers.json (content-automation format)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output', '-o',
            type=str,
            default='subscribers.json',
            help='Output file path (default: subscribers.json)',
        )
        parser.add_argument(
            '--include-inactive',
            action='store_true',
            help='Include inactive/unsubscribed entries',
        )

    def handle(self, *args, **options):
        qs = Subscriber.objects.all()
        if not options['include_inactive']:
            qs = qs.filter(is_active=True)

        data = {
            'subscribers': [sub.to_export_dict() for sub in qs.order_by('subscribed_at')],
        }

        output = Path(options['output'])
        output.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )
        self.stdout.write(self.style.SUCCESS(
            f'Exported {len(data["subscribers"])} subscribers to {output}'
        ))
