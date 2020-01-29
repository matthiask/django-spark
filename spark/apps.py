from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SparkConfig(AppConfig):
    name = "spark"
    verbose_name = _("Spark")
