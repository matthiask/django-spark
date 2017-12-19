from django.core.management.base import BaseCommand

from spark import api


class Command(BaseCommand):
    help = 'Sends all registered models through all event sources'

    def handle(self, **options):
        for model, sources in api.MODEL_SOURCES.items():
            for source in sources:
                for instance in model.objects.all():
                    api.process_events(source(instance))
