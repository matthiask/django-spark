from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SparkMailsConfig(AppConfig):
    name = "spark.spark_mails"
    verbose_name = _("Spark mails")
