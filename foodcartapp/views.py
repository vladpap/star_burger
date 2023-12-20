import json
import re

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
    try:
        data = request.data
    except ValueError:
        return Response({
            'error': 'bla bla bla',
            'valueerror': ValueError
        })

    print(f'-=-=-=-=-=-=-=-=\nData: {data}')
    if 'products' not in data:
        return Response({
            'error': 'products: Обязательное поле.'
        })
    if not data['products']:
        return Response({
            'error': 'products: Это поле не может быть пустым.'
        })

    if type(data['products']) is not list:
        return Response({
            'error': 'products: Ожидался list со значениями.'
        })

    elif len(data['products']) == 0:
        return Response({
            'error': 'products: Этот список не может быть пустым.'
        })

    if 'firstname' not in data or 'lastname' not in data or 'phonenumber' not in data or 'address' not in data:

        return Response({
            'firstname, lastname, phonenumber, address: Обязательное поле.'
        })

    if not data['firstname']:
        return Response({
            'firstname: Это поле не может быть пустым.'
        })

    if not data['lastname']:
        return Response({
            'lastname: Это поле не может быть пустым.'
        })

    if not data['phonenumber']:
        return Response({
            'phonenumber: Это поле не может быть пустым.'
        })

    if not data['address']:
        return Response({
            'address: Это поле не может быть пустым.'
        })

    if type(data['firstname']) is not str:
        return Response({
            'error': 'firstname: Not a valid string.'
        })

    if type(data['lastname']) is not str:
        return Response({
            'error': 'lastname: Not a valid string.'
        })

    if type(data['address']) is not str:
        return Response({
            'address: Not a valid string.'
        })

    if not re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', data['phonenumber']):
        return Response({
            'phonenumber': 'Введен некорректный номер телефона.'
        })

    make_order = MakeOrder.objects.create(
        first_name=data['firstname'],
        last_name=data['lastname'],
        address=data['address'],
        contact_phone=data['phonenumber']
    )

    for product in data['products']:
        
        product_id = product['product']
        try:
            product = Product.objects.get(id=product_id)
        except:
            return Response({
                f'products: Недопустимый первичный ключ {product_id}'
            })

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
