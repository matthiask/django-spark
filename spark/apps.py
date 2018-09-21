from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SparkConfig(AppConfig):
    name = "spark"
    verbose_name = _("Spark")
