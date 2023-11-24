import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import MakeOrder, Product, ProductOrder


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


@api_view(['POST'])
def register_order(request):
    # TODO это лишь заглушка
    try:
        data = request.data
    except ValueError:
        return Response({
            'error': 'bla bla bla',
            'valueerror': ValueError
        })

    make_order = MakeOrder.objects.create(
        first_name=data['firstname'],
        last_name=data['lastname'],
        address=data['address'],
        contact_phone=data['phonenumber']
    )

    for product in data['products']:
        ProductOrder.objects.create(
            order=make_order,
            product= Product.objects.get(id=product['product']),
            quantity=product['quantity']
        )

    return Response({})

# {'products': [{'product': 2, 'quantity': 1},
#               {'product': 3, 'quantity': 2},
#               {'product': 6, 'quantity': 1}],
# 'firstname': 'Владимир',
# 'lastname': 'Папин',
# 'phonenumber': '89660955537',
# 'address': 'ул. Адмиралтейская 51, '}
