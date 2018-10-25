from django.test import TestCase

from spark.spark_generators.models import CONTEXTS, Generator, events_from_generators

from testapp.models import Stuff


CONTEXTS["stuff"] = {
    "candidates": lambda: Stuff.objects.all(),
    "variables": lambda instance: {
        "key": instance.key,
        "key_length": len(instance.key),
    },
    "event": lambda instance, generator, **kwargs: {
        "group": generator["group"],
        "key": "{generator[group]}_{instance.id}".format(
            generator=generator, instance=instance
        ),
        "stuff": instance,
        **kwargs,
    },
}


class GeneratorsTestCase(TestCase):
    def test_generators(self):
        g = Generator.objects.create(context="stuff", group="stuff_bla")
        g.conditions.create(variable="key_length", type=">", value=5)

        for x in range(1, 11):
            Stuff.objects.create(key="".join(["x"] * x))

        # challenges, donations, stuffs, and inserts with savepoints and releases
        with self.assertNumQueries(3 + 3 * 5):
            events = list(events_from_generators())

        self.assertEqual(len(events), 5)
        self.assertTrue(events[0]["key"].startswith("stuff_bla_"))
        self.assertEqual(events[0]["variables"], {"key": "xxxxxx", "key_length": 6})

        # as above but including rollbacks (4 per event, not just 3)
        with self.assertNumQueries(3 + 4 * 5):
            events = list(events_from_generators())

        self.assertEqual(len(events), 0)

    def test_memoization(self):
        Generator.objects.create(context="stuff", group="group1")
        Generator.objects.create(context="stuff", group="group2")
        stuff = Stuff.objects.create(key="test")

        # generators, conditions and stuffs are only queried once
        with self.assertNumQueries(3 + 3 * 2):
            events = list(events_from_generators())

        self.assertEqual(
            set(event["key"] for event in events),
            set(("group1_{}".format(stuff.pk), "group2_{}".format(stuff.pk))),
        )
