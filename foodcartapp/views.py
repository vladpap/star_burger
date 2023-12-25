from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import (CharField, ModelSerializer, Serializer,
                                        ValidationError)

from .models import MakeOrder, Product, ProductOrder


class ApplicationSerializer(Serializer):
    contact_phone = CharField()
    ticket_type = CharField()


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


class MakeOrderSerialezer(ModelSerializer):
    class Meta:
        model = MakeOrder
        fields = '__all__'


class ProductOrderSerializer(ModelSerializer):

    class Meta:
        model = ProductOrder
        fields = ['product', 'quantity']


class OrderSerializer(Serializer):
    firstname = CharField(label='Имя', max_length=50)
    lastname = CharField(label='Фамилия', max_length=50)
    address = CharField(label='Адрес', max_length=50)
    phonenumber = CharField(
        label='Контактный телефон',
        max_length=128)
    products = ProductOrderSerializer(many=True, allow_empty=False)

    def validate_phonenumber(self, value):
        """Tracker phone number validation."""
        try:
            validate_international_phonenumber(value)
        except ValidationError:
            raise ValidationError('Phone number is not valid.')
        return value


@api_view(['POST'])
@transaction.atomic
def register_order(request):
    try:
        data = request.data
    except ValueError:
        return Response({
            'error': 'bla bla bla',
            'valueerror': ValueError
        })

    serializer = OrderSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    make_order = MakeOrder.objects.create(
        first_name=serializer.validated_data['firstname'],
        last_name=serializer.validated_data['lastname'],
        address=serializer.validated_data['address'],
        contact_phone=serializer.validated_data['phonenumber']
    )

    for product in serializer.validated_data['products']:

        ProductOrder.objects.create(
            order=make_order,
            product=product['product'],
            quantity=product['quantity'],
            price=product['product'].price
        )
    order_serializer = MakeOrderSerialezer(make_order)
    return Response(order_serializer.data)
