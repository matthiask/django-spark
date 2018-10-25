from django.db import IntegrityError, models, transaction
from django.utils.translation import ugettext_lazy as _


class EventQuerySet(models.QuerySet):
    def create_if_new(self, event):
        context = dict(event)
        try:
            with transaction.atomic():
                return self.create(
                    key=context.pop("key"),
                    group=context.pop("group"),
                    context=repr(context),
                )
        except IntegrityError:
            return None


class Event(models.Model):
    key = models.CharField(_("key"), max_length=100, primary_key=True)
    group = models.CharField(_("group"), max_length=50, db_index=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    context = models.TextField(_("context"), blank=True)

    objects = EventQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("event")
        verbose_name_plural = _("events")

    def __str__(self):
        return self.key
