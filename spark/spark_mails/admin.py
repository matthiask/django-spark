from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from .models import Mail


@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    list_display = ["event_group"]
    ordering = ["event_group"]

    def get_readonly_fields(self, request, obj=None):
        return [] if obj is None else ["rendered"]

    def rendered(self, instance):
        try:
            return format_html(
                '<div style="white-space:pre-wrap; max-width:40rem">'
                "<code>{}\n\n{}</code></div>",
                *instance.render({}),
            )
        except Exception:
            return format_html('<div style="color:red">INVALID</div>')

    rendered.short_description = _("rendered")
