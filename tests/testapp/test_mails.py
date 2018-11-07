from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core import mail
from django.test import Client, TestCase

from spark.api import only_new_events
from spark.spark_mails import api
from spark.spark_mails.models import Mail

from testapp.models import Stuff


MAIL = """
    \

Dear {{ user }}

This is the key: {{ key }} ({{ key_length }})

Best regards
"""


class MailsTestCase(TestCase):
    def test_mails(self):
        m = Mail.objects.create(event_group="stuff_mail", template_source=MAIL)
        m.full_clean()  # no exceptions

        user = User.objects.create(username="test", email="test@example.com")

        stuff = Stuff.objects.create(key="asdf")

        kwargs = m.render(
            {"user": user, "key": stuff.key, "key_length": len(stuff.key)}
        )

        self.assertEqual(kwargs["subject"], "Dear test")
        self.assertEqual(kwargs["body"], "This is the key: asdf (4)\n\nBest regards")

        events = [
            {
                "group": "stuff_mail",
                "key": "stuff_mail_1",
                "context": {
                    "key": stuff.key,
                    "key_length": len(stuff.key),
                    "user": user,
                    "spark_mail": {"to": [user.email]},
                },
            },
            {"group": "stuff_stuff", "key": "stuff_stuff_1", "context": {}},
        ]

        api.process_mail_events(only_new_events(events))
        api.process_mail_events(only_new_events(events))  # Twice.

        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.to, [user.email])
        self.assertEqual(sent.subject, "Dear test")

    def test_invalid_mail(self):
        m = Mail(event_group="test", template_source="""{{ Bla.21342._"*32424 }}""")
        self.assertEqual("{}".format(m), "test")

        with self.assertRaises(ValidationError) as cm:
            m.full_clean()

        messages = cm.exception.message_dict
        self.assertEqual(list(messages.keys()), ["template_source"])
        self.assertTrue(
            messages["template_source"][0].startswith(
                "Variables and attributes may not begin with underscores"
            )
        )

    def test_no_template(self):
        user = User.objects.create(username="test", email="test@example.com")
        events = [
            {
                "group": "stuff_mail",
                "key": "stuff_mail_1",
                "context": {"user": user, "spark_mail": {"to": [user.email]}},
            },
            {"group": "stuff_stuff", "key": "stuff_stuff_1", "context": {}},
        ]

        api.process_mail_events(only_new_events(events))
        api.process_mail_events(only_new_events(events))  # Twice.

        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.to, [user.email])

    def test_lazyness(self):
        # mails, two events
        user = User.objects.create(username="test", email="test@example.com")
        with self.assertNumQueries(4):
            api.process_mail_events(
                only_new_events(
                    [
                        {
                            "group": "stuff_mail",
                            "key": "stuff_mail_1",
                            "context": {
                                "user": user,
                                "spark_mail": {"to": [user.email]},
                            },
                        }
                    ]
                )
            )
        with self.assertNumQueries(3):  # No mails, but an event
            api.process_mail_events(
                only_new_events(
                    [
                        {
                            "group": "stuff_mail",
                            "key": "stuff_mail_2",
                            "context": {"user": user},
                        }
                    ]
                )
            )

    def test_admin(self):
        user = User.objects.create_superuser("admin", "admin@example.com", "admin")
        client = Client()
        client.force_login(user)

        response = client.get("/admin/spark_mails/mail/add/")
        self.assertNotContains(response, "rendered")

        m = Mail.objects.create(
            event_group="test", template_source="""{{ Bla.21342._"*32424 }}"""
        )
        response = client.get("/admin/spark_mails/mail/{}/change/".format(m.pk))
        self.assertContains(response, '<div style="color:red">INVALID</div>')

        m = Mail.objects.create(event_group="stuff_mail", template_source=MAIL)
        response = client.get("/admin/spark_mails/mail/{}/change/".format(m.pk))
        self.assertContains(response, "Best regards</code></div>")

    def test_empty_template(self):
        Mail.objects.create(event_group="stuff_mail", template_source="")
        user = User.objects.create(username="test", email="test@example.com")
        stuff = Stuff.objects.create(key="asdf")
        events = [
            {
                "group": "stuff_mail",
                "key": "stuff_mail_2",
                "context": {
                    "key": stuff.key,
                    "key_length": len(stuff.key),
                    "user": user,
                    "spark_mail": {
                        "to": [user.email],
                        "subject": "Would be overridden if template had content",
                    },
                },
            },
            {"group": "stuff_stuff", "key": "stuff_stuff_1", "context": {}},
        ]
        api.process_mail_events(only_new_events(events))
        api.process_mail_events(only_new_events(events))  # Twice.

        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.to, [user.email])
        self.assertEqual(sent.subject, "Would be overridden if template had content")

    def test_crashing_template(self):
        def crash():
            raise ValueError("Crash me please")

        Mail.objects.create(event_group="stuff_mail", template_source="{{ hello }}")
        events = [
            {
                "group": "stuff_mail",
                "key": "stuff_mail_3",
                "context": {
                    "hello": crash,
                    "spark_mail": {
                        "to": ["hello@example.com"],
                        "subject": "Would be overridden",
                        "body": "Yes.",
                    },
                },
            }
        ]
        api.process_mail_events(only_new_events(events))
        api.process_mail_events(only_new_events(events))  # Twice.

        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.to, ["hello@example.com"])
        self.assertEqual(sent.subject, "Would be overridden")
        self.assertEqual(sent.body, "Yes.")
