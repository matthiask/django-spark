from django import forms
from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from .api import SOURCES
from .models import Condition, Generator


class ConditionInline(admin.TabularInline):
    model = Condition
    extra = 0


class SourceSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        kwargs["choices"] = [("", "----------")] + list(
            sorted(
                (
                    (key, capfirst(source.get("verbose_name", key)))
                    for key, source in SOURCES.items()
                ),
                key=lambda row: row[1],
            )
        )
        super().__init__(*args, **kwargs)


@admin.register(Generator)
class GeneratorAdmin(admin.ModelAdmin):
    inlines = [ConditionInline]
    list_display = ["group", "source", "get_conditions_display"]
    ordering = ["source", "group"]

    def get_queryset(self, request):
        return self.model.objects.prefetch_related("conditions")

    def get_conditions_display(self, instance):
        return " && ".join(str(condition) for condition in instance.conditions.all())

    get_conditions_display.short_description = _("conditions")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "source":
            kwargs["widget"] = SourceSelect()
        return super().formfield_for_dbfield(db_field, request=request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        return ["description"] if obj and obj.source in SOURCES else []

    def description(self, instance):
        source = SOURCES[instance.source]
        context = source["context"]
        if not hasattr(context, "context_description"):
            return _("Description not available.")
        return format_html(
            "{} {}",
            _('The "%s" source provides the following context:')
            % capfirst(source.get("verbose_name", instance.source)),
            format_html_join(
                "", "<br><strong>{}</strong>: {}", context.context_description
            ),
        )

    description.short_description = capfirst(_("description"))

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)
