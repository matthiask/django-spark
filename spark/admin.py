from django.contrib import admin

from spark.models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("key", "group", "created_at", "context")
    list_filter = ("group", "created_at")
