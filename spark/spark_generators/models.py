import operator

from django.db import models
from django.utils.translation import ugettext_lazy as _

from spark.models import Event


CONTEXTS = {}


class Generator(models.Model):
    group = models.CharField(_("group"), max_length=50)
    context = models.CharField(_("context"), max_length=50, choices=[("", "")])

    class Meta:
        verbose_name = _("generator")
        verbose_name_plural = _("generators")

    def __str__(self):
        return self.group

    def as_generator(self):
        return {
            "group": self.group,
            "context": self.context,
            "conditions": [
                condition.as_condition() for condition in self.conditions.all()
            ],
        }


class Condition(models.Model):
    TYPES = [
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
    type = models.CharField(
        _("type"), max_length=10, choices=[(d, d) for d, op in TYPES]
    )
    value = models.IntegerField(_("value"))

    class Meta:
        ordering = ["pk"]
        verbose_name = _("condition")
        verbose_name_plural = _("conditions")

    def __str__(self):
        return "{o.variable} {o.type} {o.value}".format(o=self)

    def as_condition(self):
        op = dict(self.TYPES)[self.type]
        return {"variable": self.variable, "test": lambda v: op(v, self.value)}


def pure_function_memoizer():
    MEMO = {}

    def call(fn, *args):
        key = (fn, *args)
        if key not in MEMO:
            MEMO[key] = fn(*args)
        return MEMO[key]

    return call


def events_from_generators(queryset=None):
    if queryset is None:
        queryset = Generator.objects.all()

    memoizer = pure_function_memoizer()

    for generator in queryset.prefetch_related("conditions"):
        g = generator.as_generator()

        context = CONTEXTS[g["context"]]
        candidates = memoizer(context["candidates"])
        for candidate in candidates:
            variables = context["variables"](candidate)
            for condition in g["conditions"]:
                if condition["variable"] not in variables:
                    break
                if not condition["test"](variables[condition["variable"]]):
                    break
            else:
                e = context["event"](
                    instance=candidate, generator=g, variables=variables
                )
                if Event.objects.create_if_new(e):
                    yield e
