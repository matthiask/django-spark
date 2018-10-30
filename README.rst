==========================================
django-spark - Event sourcing and handling
==========================================

.. image:: https://travis-ci.org/matthiask/django-spark.png?branch=master
   :target: https://travis-ci.org/matthiask/django-spark

Version |release|

This is not supposed to be real documentation; it's more a reminder for
myself.

The idea is that there are event sources and event handlers. Event
sources may create a stream of ``spark.api.Event`` instances, where each
event must have a ``group`` and a ``key``. Additional data may be added
to the ``Event`` as well. Keys are globally unique -- events with the
same key are still only processed exactly once. Groups are used to
determine which handlers handle a certain event.

Event handlers are functions which are called once per
``spark.api.Event`` instance if the event's group matches the event
handler's regex.


Some usage example code
=======================

Given a challenge, create events for the challenge (the specifics do not
matter):

.. code-block:: python

    from datetime import date
    from spark import api

    def events_from_challenge(challenge):
        if not challenge.is_active:
            return

        context = {"challenge": challenge}

        yield api.event("challenge_created", challenge.pk, context)

        if (date.today() - challenge.start_date).days > 2:
            if challenge.donations.count() < 2:
                yield api.event("challenge_inactivity_2d", challenge.pk, context)

        if (challenge.end_date - date.today()).days <= 2:
            yield api.event("challenge_ends_2d", challenge.pk, context)

        if challenge.end_date < date.today():
            yield api.event("challenge_ended", challenge.pk, context)


Send mails related to challenges (uses django-authlib's
``render_to_mail``):

.. code-block:: python

    from authlib.email import render_to_mail

    def send_challenge_mail(event):
        challenge = event["context"]["challenge"]
        render_to_mail(
            # Different mail text per event group:
            "challenges/mails/%s" % event["group"],
            {
                "challenge": challenge,
            },
            to=[challenge.user.email],
        ).send(fail_silently=True)


Register the handlers:

.. code-block:: python

    from spark import api

    class ChallengesConfig(AppConfig):
        def ready(self):
            api.register_group_handler(
                handler=send_challenge_mail,
                group=r'^challenge',
            )

            Challenge = self.get_model('Challenge')

            # All this does right now is register a post_save signal
            # handler which runs the challenge instance through
            # events_from_challenge and processes the events:
            api.register_model_event_source(
                sender=Challenge,
                source=events_from_challenge,
            )


Now, events are generated and handled directly in process.
Alternatively, you might want to handle events outside the
request-response cycle. This can be achieved by only registering the
model event source e.g. in a management command, and then sending all
model instances through all event sources, and directly processing those
events, for example like this:

.. code-block:: python

    from spark import api

    api.register_model_event_source(...)

    # Copied from the process_spark_sources management command inside
    # this repository
    for model, sources in api.MODEL_SOURCES.items():
        for instance in model.objects.all():
            for source in sources:
                api.process_events(api.only_new_events(source(instance)))


- `Documentation <https://django-spark.readthedocs.io>`_
- `Github <https://github.com/matthiask/django-spark/>`_
