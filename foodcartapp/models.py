from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from phonenumber_field.modelfields import PhoneNumberField

from django.urls import reverse


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = PhoneNumberField(
        'контактный телефон',
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class MakeOrderQuerySet(models.QuerySet):
    def with_amount(self):
        return MakeOrder \
            .objects \
            .annotate(amount=Sum(
                F('products__quantity') * F('products__price'))) \
            .order_by('-id')


class MakeOrder(models.Model):

    class ChoicesStatus(models.TextChoices):
        COMPLETED = 'Завершен', 'Завершен'
        COURIER = 'У курьера', 'У курьера'
        COOK = 'Готовится', 'Готовится'
        APPROVED = 'Утвержденный', 'Утвержденный'
        UNPROCESSED = 'Необработанный', 'Необработанный'

    first_name = models.CharField(
        'Имя',
        max_length=50
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=50
    )
    address = models.CharField(
        'Адрес',
        max_length=50
    )
    contact_phone = PhoneNumberField(
        verbose_name='контактный телефон',
        db_index=True,
    )
    status = models.CharField(
        verbose_name='статус',
        default=ChoicesStatus.UNPROCESSED,
        max_length=20,
        choices=ChoicesStatus.choices,
        db_index=True
    )

    objects = MakeOrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Оформление заказа'
        verbose_name_plural = 'Оформленные заказы'

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.address}'


class ProductOrder(models.Model):
    order = models.ForeignKey(
        MakeOrder,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='ordering',
        verbose_name='продукт',
    )
    quantity = models.IntegerField(
        verbose_name='количество'
    )
    price = models.DecimalField(
        'цена',
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Продукт в заказе'
        verbose_name_plural = 'Продуктов в заказе'

    def __str__(self):
        return self.order.first_name
