import operator

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Generator(models.Model):
    group = models.CharField(_("group"), max_length=50)
    source = models.CharField(_("source"), max_length=50)

    class Meta:
        verbose_name = _("generator")
        verbose_name_plural = _("generators")

    def __str__(self):
        return self.group

    def as_generator(self):
        return {
            "group": self.group,
            "source": self.source,
            "conditions": [
                condition.as_condition() for condition in self.conditions.all()
            ],
        }


class Condition(models.Model):
    OPERATORS = [
        (">", operator.gt),
        ("<", operator.lt),
        (">=", operator.ge),
        ("<=", operator.le),
        ("=", operator.eq),
        ("!=", operator.ne),
    ]

    generator = models.ForeignKey(
        Generator,
        on_delete=models.CASCADE,
        related_name="conditions",
        verbose_name=_("generator"),
    )
    variable = models.CharField(_("variable"), max_length=50)
    operator = models.CharField(
        _("operator"), max_length=10, choices=[(d, d) for d, op in OPERATORS]
    )
    value = models.IntegerField(_("value"))

    class Meta:
        ordering = ["pk"]
        verbose_name = _("condition")
        verbose_name_plural = _("conditions")

    def __str__(self):
        return "{o.variable} {o.operator} {o.value}".format(o=self)

    def as_condition(self):
        op = dict(self.OPERATORS)[self.operator]
        return {"variable": self.variable, "test": lambda v: op(v, self.value)}
