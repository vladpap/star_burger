from django.db import transaction
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework.serializers import ModelSerializer, ValidationError

from .models import Order, OrderItem


class OrderItemSerializer(ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):

    products = OrderItemSerializer(many=True, allow_empty=False)

    def validate_phonenumber(self, value):
        """Tracker phone number validation."""
        try:
            validate_international_phonenumber(value)
        except ValidationError:
            raise ValidationError('Phone number is not valid.')
        return value

    class Meta:
        model = Order
        fields = [
            'firstname',
            'lastname',
            'address',
            'phonenumber',
            'products',
        ]

    @transaction.atomic
    def create(self, validated_data):
        order = Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            address=validated_data['address'],
            phonenumber=validated_data['phonenumber'],
        )
        products = validated_data['products']

        items = [OrderItem(
            order=order,
            price=fields['product'].price,
            **fields) for fields in products]

        OrderItem.objects.bulk_create(items)

        return order
