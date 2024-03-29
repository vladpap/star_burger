# Generated by Django 4.2.7 on 2024-02-14 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0049_makeorder_cook_restaurant_alter_makeorder_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='latitude',
            field=models.FloatField(blank=True, default=None, null=True, verbose_name='широта'),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='longitude',
            field=models.FloatField(blank=True, default=None, null=True, verbose_name='долгота'),
        ),
    ]
