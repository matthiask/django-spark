from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from . import models


class ConditionInline(admin.TabularInline):
    model = models.Condition
    extra = 0


@admin.register(models.Generator)
class GeneratorAdmin(admin.ModelAdmin):
    inlines = [ConditionInline]
    list_display = ["group", "context", "get_conditions_display"]
    ordering = ["context", "group"]

    def get_queryset(self, request):
        return self.model.objects.prefetch_related("conditions")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "context":
            kwargs["widget"] = forms.Select(
                choices=[(v, v) for v in sorted(models.CONTEXTS)]
            )
        return super().formfield_for_dbfield(db_field, request=request, **kwargs)

    def get_conditions_display(self, instance):
        return " && ".join(str(condition) for condition in instance.conditions.all())

    get_conditions_display.short_description = _("conditions")
