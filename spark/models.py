from django.db import models
from django.utils.translation import ugettext_lazy as _


class Event(models.Model):
    key = models.CharField(_("key"), max_length=100, primary_key=True)
    group = models.CharField(_("group"), max_length=50, db_index=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    context = models.TextField(_("context"), blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("event")
        verbose_name_plural = _("events")

    def __str__(self):
        return self.key
