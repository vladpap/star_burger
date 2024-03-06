from django.db import models


class GeoLocation(models.Model):
    address = models.CharField(
        'адрес',
        max_length=80,
        unique=True
    )
    latitude = models.FloatField(
        verbose_name='широта',
        null=True
    )
    longitude = models.FloatField(
        verbose_name='долгота',
        null=True
    )

    class Meta:
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'
        unique_together = [
            ['address']
        ]

    def __str__(self):
        return f'Адрес:{self.address} д: {self.longitude} ш: {self.latitude}'
