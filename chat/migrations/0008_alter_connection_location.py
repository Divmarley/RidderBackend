# Generated by Django 4.2.14 on 2024-08-05 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0007_driveronline_push_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connection',
            name='location',
            field=models.JSONField(),
        ),
    ]