# Generated by Django 4.2.7 on 2024-02-15 19:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0051_makeorder_latitude_makeorder_longitude_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='makeorder',
            name='restaurant_distance',
        ),
    ]