# Generated by Django 4.2.7 on 2023-12-26 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_makeorder_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='makeorder',
            name='comment',
            field=models.TextField(blank=True, verbose_name='комментарий'),
        ),
    ]
