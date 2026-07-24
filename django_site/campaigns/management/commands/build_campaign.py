from django.core.management.base import BaseCommand

from campaigns.services import build_weekly_campaign, send_campaign


class Command(BaseCommand):
    help = 'Build or send newsletter campaign'

    def add_arguments(self, parser):
        parser.add_argument('--send', action='store_true', help='Send latest draft')
        parser.add_argument('--campaign-id', type=int)

    def handle(self, *args, **options):
        if options['send']:
            from campaigns.models import NewsletterCampaign
            if options['campaign_id']:
                campaign = NewsletterCampaign.objects.get(pk=options['campaign_id'])
            else:
                campaign = NewsletterCampaign.objects.filter(status='draft').order_by('-created_at').first()
            if not campaign:
                self.stderr.write('No draft campaign found')
                return
            n = send_campaign(campaign)
            self.stdout.write(self.style.SUCCESS(f'Sent to {n} subscribers'))
        else:
            c = build_weekly_campaign()
            self.stdout.write(self.style.SUCCESS(f'Draft campaign #{c.pk} created'))
