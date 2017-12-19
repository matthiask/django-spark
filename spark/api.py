import re
import types

from django.db import IntegrityError, transaction
from django.db.models import signals


MODEL_SOURCES = {}
HANDLERS = []


# Good enough for now.
Event = types.SimpleNamespace


def process_events(iterable):
    from spark.models import Event as RealEvent

    for event in iterable:
        try:
            with transaction.atomic():
                RealEvent.objects.create(
                    key=event.key,
                    group=event.group,
                    context=repr(getattr(event, 'context', {})),
                )
        except IntegrityError:
            pass
        else:
            for group, handler in HANDLERS:
                if re.search(group, event.group):
                    handler(event)


def create_post_save_handler(source):
    def on_post_save(sender, instance, **kwargs):
        process_events(source(instance))
    return on_post_save


def register_model_event_source(*, sender, source):
    MODEL_SOURCES.setdefault(sender, []).append(source)

    signals.post_save.connect(
        create_post_save_handler(source),
        sender=sender,
        weak=False,
    )


def register_group_handler(*, group, handler):
    HANDLERS.append((group, handler))
