# Generated by Django 4.2.7 on 2023-12-26 06:35

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_makeorder_called_at_makeorder_delivered_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='makeorder',
            name='registrate_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='создан'),
        ),
    ]
