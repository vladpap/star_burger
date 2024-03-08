from django.db import transaction
from rest_framework.serializers import ModelSerializer

from .models import Order, OrderItem


class OrderItemSerializer(ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):

    products = OrderItemSerializer(many=True, allow_empty=False)

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
