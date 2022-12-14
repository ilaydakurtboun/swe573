# Generated by Django 3.1.1 on 2022-11-20 13:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Label",
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
                ("name", models.CharField(default="", max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name="Space",
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
                ("title", models.CharField(default="", max_length=300)),
                (
                    "description",
                    models.CharField(blank=True, default="", max_length=300, null=True),
                ),
                ("created_time", models.DateTimeField(auto_now_add=True)),
                (
                    "owner",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="own_spaces",
                        to="user.user",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Post",
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
                ("title", models.CharField(default="", max_length=300)),
                (
                    "description",
                    models.CharField(blank=True, default="", max_length=300, null=True),
                ),
                ("platform", models.CharField(default="", max_length=300)),
                ("link", models.CharField(default="", max_length=300)),
                ("image", models.FileField(blank=True, null=True, upload_to="posts")),
                (
                    "is_private",
                    models.BooleanField(blank=True, default=False, null=True),
                ),
                ("created_time", models.DateTimeField(auto_now_add=True)),
                (
                    "label",
                    models.ManyToManyField(blank=True, null=True, to="feed.Label"),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="own_posts",
                        to="user.user",
                    ),
                ),
            ],
        ),
    ]
