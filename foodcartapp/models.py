from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=80,
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


class OrderQuerySet(models.QuerySet):
    def with_amount(self):
        return Order \
            .objects \
            .annotate(amount=Sum(
                F('products__quantity') * F('products__price'))) \
            .order_by('-id')


class Order(models.Model):

    class ChoicesStatus(models.TextChoices):
        COMPLETED = (10, 'Завершен')
        COURIER = (20, 'У курьера')
        COOK = (30, 'Готовится')
        UNPROCESSED = (90, 'Необработанный')

    class ChoicesPaymentMethod(models.TextChoices):
        CARD = 'Картой', 'Картой'
        CASH = 'Наличные', 'Наличные'
        NOT_SPECIFIED = 'Не указан', 'Не указан'

    firstname = models.CharField(
        'Имя',
        max_length=50
    )
    lastname = models.CharField(
        'Фамилия',
        max_length=50
    )
    address = models.CharField(
        'Адрес',
        max_length=80
    )
    phonenumber = PhoneNumberField(
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
    payment_method = models.CharField(
        verbose_name='способ оплаты',
        default=ChoicesPaymentMethod.NOT_SPECIFIED,
        max_length=20,
        choices=ChoicesPaymentMethod.choices,
        db_index=True
    )
    comment = models.TextField(
        verbose_name='комментарий',
        blank=True
    )
    registrate_at = models.DateTimeField(
        verbose_name='создан',
        default=timezone.now,
        db_index=True
    )
    called_at = models.DateTimeField(
        verbose_name='звонок',
        blank=True,
        null=True,
        db_index=True
    )
    delivered_at = models.DateTimeField(
        verbose_name='доставлен',
        blank=True,
        null=True,
        db_index=True
    )
    cook_restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
        verbose_name='Готовиться в',
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Оформление заказа'
        verbose_name_plural = 'Оформленные заказы'
        ordering = ['-status', 'id']

    @property
    def full_name(self):
        return '%s %s' % (self.firstname, self.lastname)

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
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
        verbose_name='количество',
        validators=[MinValueValidator(1)]
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
        return self.order.firstname


@receiver(pre_save, sender=Order)
def order_pre_saved(sender, instance,  **kwargs):
    old_cook_restaurant = (
        instance.id
        and
        Order.objects.get(id=instance.id).cook_restaurant)

    if instance.cook_restaurant != old_cook_restaurant:
        instance.status = Order.ChoicesStatus.COOK
