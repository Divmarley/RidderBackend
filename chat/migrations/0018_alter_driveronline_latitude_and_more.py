# Generated by Django 4.2.14 on 2024-08-11 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0017_alter_driveronline_latitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driveronline',
            name='latitude',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='driveronline',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='driveronline',
            name='longitude',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]