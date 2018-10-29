from django.contrib.auth.models import User
from django.test import Client, TestCase

from spark.api import only_new_events
from spark.spark_generators import api
from spark.spark_generators.models import Generator

from testapp.models import Stuff


def stuff_context(instance):
    return {"stuff": instance, "key": instance.key, "key_length": len(instance.key)}


api.SOURCES["stuff"] = {
    "candidates": lambda: Stuff.objects.all(),
    "context": stuff_context,
}


def new_events_from_generators():
    return only_new_events(api.events_from_generators())


class GeneratorsTestCase(TestCase):
    def test_generators(self):
        g = Generator.objects.create(source="stuff", group="stuff_bla")
        g.conditions.create(variable="key_length", operator=">", value=5)

        stuffs = [Stuff.objects.create(key="".join(["x"] * x)) for x in range(1, 11)]

        # challenges, donations, stuffs, and inserts with savepoints and releases
        with self.assertNumQueries(3 + 3 * 5):
            events = list(new_events_from_generators())

        self.assertEqual(len(events), 5)
        self.assertTrue(events[0]["key"].startswith("stuff_bla_"))
        self.assertEqual(events[0]["context"]["stuff"], stuffs[5])
        self.assertEqual(events[0]["context"]["key"], "xxxxxx")
        self.assertEqual(events[0]["context"]["key_length"], 6)

        # as above but including rollbacks (4 per event, not just 3)
        with self.assertNumQueries(3 + 4 * 5):
            events = list(new_events_from_generators())

        self.assertEqual(len(events), 0)

    def test_memoization(self):
        Generator.objects.create(source="stuff", group="group1")
        Generator.objects.create(source="stuff", group="group2")
        stuff = Stuff.objects.create(key="test")

        # generators, conditions and stuffs are only queried once
        with self.assertNumQueries(3 + 3 * 2):
            events = list(new_events_from_generators())

        self.assertEqual(
            set(event["key"] for event in events),
            set(("group1_{}".format(stuff.pk), "group2_{}".format(stuff.pk))),
        )

    def test_not_exists(self):
        g = Generator.objects.create(source="stuff", group="stuff_bla")
        g.conditions.create(variable="NOT_EXISTS", operator=">", value=5)

        Stuff.objects.create(key="test")

        # No queries for creating stuffs ... all are skipped
        with self.assertNumQueries(3):
            events = list(new_events_from_generators())

        self.assertEqual(events, [])

    def test_admin(self):
        g = Generator.objects.create(source="stuff", group="stuff_bla")
        g.conditions.create(variable="key_length", operator=">", value=5)

        user = User.objects.create_superuser("admin", "admin@example.com", "admin")
        client = Client()
        client.force_login(user)

        response = client.get("/admin/spark_generators/generator/")
        self.assertContains(response, ">stuff_bla</a>")
        self.assertContains(response, "key_length &gt; 5")

        response = client.get(
            "/admin/spark_generators/generator/{}/change/".format(g.pk)
        )
        self.assertContains(
            response,
            """
            <select name="source" maxlength="50" required id="id_source">
            <option value="">----------</option>
            <option value="stuff" selected>Stuff</option>
            </select>
            """,
            html=True,
        )
        self.assertContains(response, "field-description")
        self.assertContains(response, "Description not available.")
        self.assertContains(response, 'id="conditions-group"')

        stuff_context.context_description = [
            ("key", "The instance's key"),
            ("key_length", "The key length in chars"),
        ]
        response = client.get(
            "/admin/spark_generators/generator/{}/change/".format(g.pk)
        )
        self.assertContains(
            response, "<br><strong>key_length</strong>: The key length in chars</div>"
        )

        response = client.get("/admin/spark_generators/generator/add/")
        self.assertNotContains(response, "field-description")
        self.assertNotContains(response, 'id="conditions-group"')
