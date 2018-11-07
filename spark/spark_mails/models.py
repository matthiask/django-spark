from django.core.exceptions import ValidationError
from django.db import models
from django.template import Context, Template
from django.utils.functional import cached_property, lazy
from django.utils.translation import ugettext_lazy as _


class MailQuerySet(models.QuerySet):
    def as_mails(self):
        return lazy(lambda: {m.event_group: m for m in self}, dict)()


class Mail(models.Model):
    event_group = models.CharField(_("event group"), max_length=50, unique=True)
    template_source = models.TextField(_("template"))

    objects = MailQuerySet.as_manager()

    class Meta:
        verbose_name = _("mail")
        verbose_name_plural = _("mails")

    def __str__(self):
        return self.event_group

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)
        exclude = exclude or []
        errors = {}

        try:
            self.template.render(Context({}))
        except Exception as exc:
            errors["template_source"] = str(exc)

        if errors:
            raise ValidationError(errors)

    @cached_property
    def template(self):
        return Template(self.template_source)

    def render(self, context):
        lines = iter(
            line.rstrip()
            for line in self.template.render(Context(context)).splitlines()
        )
        subject = ""
        try:
            while True:
                line = next(lines)
                if line:
                    subject = line
                    break
        except StopIteration:  # if lines is empty
            pass
        return subject, "\n".join(lines).strip("\n")
