from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SparkGeneratorsConfig(AppConfig):
    name = "spark.spark_generators"
    verbose_name = _("Spark generators")
