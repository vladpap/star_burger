# Generated by Django 4.2.7 on 2023-12-25 09:44

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_alter_makeorder_contact_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='productorder',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], verbose_name='цена'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='productorder',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='foodcartapp.makeorder', verbose_name='заказ'),
        ),
    ]
