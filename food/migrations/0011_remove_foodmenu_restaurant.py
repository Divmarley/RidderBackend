# Generated by Django 4.2.14 on 2024-08-18 18:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0010_alter_foodmenu_restaurant_alter_image_border_radius_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='foodmenu',
            name='restaurant',
        ),
    ]