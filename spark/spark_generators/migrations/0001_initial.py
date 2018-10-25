# Generated by Django 2.1.2 on 2018-10-25 12:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Condition",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("variable", models.CharField(max_length=50, verbose_name="variable")),
                (
                    "type",
                    models.CharField(
                        choices=[
                            (">", ">"),
                            ("<", "<"),
                            (">=", ">="),
                            ("<=", "<="),
                            ("=", "="),
                            ("!=", "!="),
                        ],
                        max_length=10,
                        verbose_name="type",
                    ),
                ),
                ("value", models.IntegerField(verbose_name="value")),
            ],
            options={
                "verbose_name": "condition",
                "verbose_name_plural": "conditions",
                "ordering": ["pk"],
            },
        ),
        migrations.CreateModel(
            name="Generator",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("group", models.CharField(max_length=50, verbose_name="group")),
                ("context", models.CharField(max_length=50, verbose_name="context")),
            ],
            options={"verbose_name": "generator", "verbose_name_plural": "generators"},
        ),
        migrations.AddField(
            model_name="condition",
            name="generator",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="conditions",
                to="spark_generators.Generator",
                verbose_name="generator",
            ),
        ),
    ]
