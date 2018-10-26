from django import forms
from django.contrib import admin
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from .api import SOURCES
from .models import Condition, Generator


class ConditionInline(admin.TabularInline):
    model = Condition
    extra = 0


@admin.register(Generator)
class GeneratorAdmin(admin.ModelAdmin):
    inlines = [ConditionInline]
    list_display = ["group", "source", "get_conditions_display"]
    ordering = ["source", "group"]

    def get_queryset(self, request):
        return self.model.objects.prefetch_related("conditions")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "source":
            kwargs["widget"] = forms.Select(
                choices=list(
                    sorted(
                        (
                            (key, capfirst(source.get("verbose_name", key)))
                            for key, source in SOURCES.items()
                        ),
                        key=lambda row: row[1],
                    )
                )
            )
        return super().formfield_for_dbfield(db_field, request=request, **kwargs)

    def get_conditions_display(self, instance):
        return " && ".join(str(condition) for condition in instance.conditions.all())

    get_conditions_display.short_description = _("conditions")
