from django.contrib import admin

from . import models


class ConditionInline(admin.TabularInline):
    model = models.Condition
    extra = 0


@admin.register(models.Generator)
class GeneratorAdmin(admin.ModelAdmin):
    inlines = [ConditionInline]
    list_display = ["group", "context_value"]
    ordering = ["group"]

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "context":
            kwargs["choices"] = [(v, v) for v in models.CONTEXTS]
        return super().formfield_for_choice_field(db_field, request=request, **kwargs)

    def context_value(self, instance):
        return instance.context
