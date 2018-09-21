import re
import types

from django.db import IntegrityError, transaction
from django.db.models import signals


MODEL_SOURCES = {}
HANDLERS = []


# Good enough for now.
class Event(types.SimpleNamespace):
    pass


def process_events(iterable):
    from spark.models import Event as E

    for e in iterable:
        try:
            with transaction.atomic():
                E.objects.create(key=e.key, group=e.group, context=repr(e))
        except IntegrityError:
            pass
        else:
            for group, handler in HANDLERS:
                if re.search(group, e.group):
                    handler(e)


def register_model_event_source(*, sender, source):
    MODEL_SOURCES.setdefault(sender, []).append(source)

    def on_post_save(sender, instance, **kwargs):
        process_events(source(instance))

    signals.post_save.connect(on_post_save, sender=sender, weak=False)


def register_group_handler(*, group, handler):
    HANDLERS.append((group, handler))
