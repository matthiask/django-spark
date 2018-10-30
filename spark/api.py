import re


MODEL_SOURCES = {}
HANDLERS = []


def event(group, instance_id, context=None):
    return {
        "group": group,
        "key": "{}_{}".format(group, instance_id),
        "context": {} if context is None else context,
    }


def only_new_events(iterable):
    from .models import Event

    for e in iterable:
        if Event.objects.create_if_new(e):
            yield e


def process_events(iterable):
    for e in iterable:
        for group, handler in HANDLERS:
            if re.search(group, e["group"]):
                handler(e)


def register_model_event_source(*, sender, source):
    from django.db.models import signals

    MODEL_SOURCES.setdefault(sender, []).append(source)

    def on_post_save(sender, instance, **kwargs):
        process_events(only_new_events(source(instance)))

    signals.post_save.connect(on_post_save, sender=sender, weak=False)


def register_group_handler(*, group, handler):
    HANDLERS.append((group, handler))
