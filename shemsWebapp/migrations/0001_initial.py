# Generated by Django 5.0 on 2023-12-18 22:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DeviceModel",
            fields=[
                (
                    "model_num",
                    models.CharField(max_length=50, primary_key=True, serialize=False),
                ),
                ("model_type", models.CharField(max_length=50)),
                ("properties", models.CharField(max_length=100)),
            ],
            options={
                "db_table": "model",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                ("lid", models.AutoField(primary_key=True, serialize=False)),
                ("num_bedrooms", models.IntegerField()),
                ("num_occupants", models.IntegerField()),
                ("area", models.IntegerField()),
                ("unit", models.CharField(max_length=20)),
                ("street", models.CharField(max_length=30)),
                ("building", models.CharField(max_length=20)),
                ("city", models.CharField(max_length=20)),
                ("zipcode", models.CharField(max_length=5)),
            ],
            options={
                "db_table": "location",
            },
        ),
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("cid", models.AutoField(primary_key=True, serialize=False)),
                ("first_name", models.CharField(max_length=30)),
                ("last_name", models.CharField(max_length=30)),
                ("billing_address", models.CharField(max_length=100)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "customer",
            },
        ),
        migrations.CreateModel(
            name="Device",
            fields=[
                ("did", models.AutoField(primary_key=True, serialize=False)),
                (
                    "model_num",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="number",
                        to="shemsWebapp.devicemodel",
                    ),
                ),
                (
                    "lid",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shemsWebapp.location",
                    ),
                ),
            ],
            options={
                "db_table": "device",
            },
        ),
        migrations.CreateModel(
            name="CustomerLocation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "cid",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shemsWebapp.customer",
                    ),
                ),
                (
                    "lid",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shemsWebapp.location",
                    ),
                ),
            ],
            options={
                "db_table": "customerlocation",
            },
        ),
    ]
