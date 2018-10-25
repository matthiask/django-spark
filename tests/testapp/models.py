from django.db import models


class Stuff(models.Model):
    key = models.CharField(max_length=10)

    class Meta:
        ordering = ["pk"]
