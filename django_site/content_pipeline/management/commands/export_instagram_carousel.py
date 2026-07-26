from django.core.management.base import BaseCommand, CommandError

from content_pipeline.instagram_export import InstagramExportError, export_carousel_pngs
from content_pipeline.models import InstagramCarousel


class Command(BaseCommand):
    help = 'Exporta slides de um carrossel Instagram para PNG 1080×1350'

    def add_arguments(self, parser):
        parser.add_argument('carousel_id', type=int, help='ID do InstagramCarousel')
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regera PNGs mesmo se já existirem',
        )

    def handle(self, *args, **options):
        carousel = InstagramCarousel.objects.filter(pk=options['carousel_id']).first()
        if not carousel:
            raise CommandError(f'Carrossel {options["carousel_id"]} não encontrado')

        try:
            paths = export_carousel_pngs(carousel, force=options['force'])
        except InstagramExportError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS(f'{len(paths)} PNG(s) em media/instagram/{carousel.pk}/'))
        for path in paths:
            self.stdout.write(f'  - {path}')
