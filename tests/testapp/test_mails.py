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

        subject, body = m.render(
            {"user": user, "key": stuff.key, "key_length": len(stuff.key)}
        )

        self.assertEqual(subject, "Dear test")
        self.assertEqual(body, "This is the key: asdf (4)\n\nBest regards")

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
