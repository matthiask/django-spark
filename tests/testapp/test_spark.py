from django.contrib.auth.models import User
from django.test import TestCase

from spark import api
from spark.models import Event

from testapp.models import Stuff


def events_from_stuff(stuff):
    yield api.Event(
        group="stuff_created",
        key="stuff_created_{}".format(stuff.pk),
        stuff=stuff,
    )


events = []
def stuff_handler(event):
    events.append(event)


def crashing_handler(event):
    raise NotImplementedError


api.register_model_event_source(sender=Stuff, source=events_from_stuff)
api.register_group_handler(handler=stuff_handler, group=r"^stuff_created")
api.register_group_handler(handler=stuff_handler, group=r"^something_else")


class SparkTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test", is_staff=True, is_superuser=True
        )

        global events
        events = []

    def test_spark(self):
        global events

        self.assertEqual(events, [])

        stuff = Stuff.objects.create(key="first")
        event = Event.objects.get()  # Exactly one

        self.assertEqual(event.key, "stuff_created_{}".format(stuff.pk))
        self.assertEqual(event.group, "stuff_created")
        self.assertEqual(event.key, "{}".format(event))

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].stuff, stuff)

        # Create some duplicates
        for stuff in Stuff.objects.all():
            events_to_process = list(events_from_stuff(stuff))
            self.assertTrue(len(events_to_process), 1)
            api.process_events(events_to_process)

        # But still only one event
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(len(events), 1)
