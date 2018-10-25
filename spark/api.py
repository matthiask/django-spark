import re

from django.db.models import signals


MODEL_SOURCES = {}
HANDLERS = []


def process_events(iterable):
    from .models import Event

    for e in iterable:
        if Event.objects.create_if_new(e):
            for group, handler in HANDLERS:
                if re.search(group, e["group"]):
                    handler(e)


def register_model_event_source(*, sender, source):
    MODEL_SOURCES.setdefault(sender, []).append(source)

    def on_post_save(sender, instance, **kwargs):
        process_events(source(instance))

    signals.post_save.connect(on_post_save, sender=sender, weak=False)


def register_group_handler(*, group, handler):
    HANDLERS.append((group, handler))
