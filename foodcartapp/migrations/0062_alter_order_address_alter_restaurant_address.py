# Generated by Django 4.2.7 on 2024-03-05 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0061_remove_restaurant_latitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.CharField(max_length=80, verbose_name='Адрес'),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='address',
            field=models.CharField(blank=True, max_length=80, verbose_name='адрес'),
        ),
    ]
