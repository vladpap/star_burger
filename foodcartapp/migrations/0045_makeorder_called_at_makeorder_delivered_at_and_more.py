# Generated by Django 4.2.7 on 2023-12-26 06:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0044_makeorder_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='makeorder',
            name='called_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='звонок'),
        ),
        migrations.AddField(
            model_name='makeorder',
            name='delivered_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='доставлен'),
        ),
        migrations.AddField(
            model_name='makeorder',
            name='registrate_at',
            field=models.DateTimeField(db_index=True, default=datetime.datetime(2023, 12, 26, 6, 30, 43, 293006, tzinfo=datetime.timezone.utc), verbose_name='создан'),
        ),
    ]