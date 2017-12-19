from django.contrib.auth.models import User
from django.test import TestCase


class SparkTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='test',
            is_staff=True,
            is_superuser=True,
        )
