from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy import distance

from foodcartapp.models import Order, Product, Restaurant
from geo_location.models import GeoLocation

from . import geo_coder


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {
            item.restaurant_id: item.availability
            for item
            in product.menu_items.all()}
        ordered_availability = [
            availability.get(restaurant.id, False)
            for restaurant
            in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability':
            products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def location_from_address(locations, address)\
            -> (bool, float | None, float | None):

    is_create = False
    lon, lat = None, None
    if address in locations.values_list('address', flat=True):
        for location in locations:
            if address == location.address:
                lon = location.longitude
                lat = location.latitude
                break
    else:
        is_create = True
        lon, lat = geo_coder.fetch_coordinates(
                settings.YANDEX_GEOCODER_KEY,
                address)
        geo_location, created = GeoLocation.objects.get_or_create(
            address=address, latitude=lat, longitude=lon)

    return is_create, lon, lat


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):

    orders = (
        Order.objects
        .with_amount()
        .exclude(status=Order.ChoicesStatus.COMPLETED)
        .order_by('-status', 'id')
        .prefetch_related('products')
        )

    location_adress = GeoLocation.objects.all()

    for order in orders:
        order.get_status = order.get_status_display()

        created, lon_order_addres, lat_order_adress = location_from_address(
            location_adress, order.address)

        order.availability_geo = True
        if lon_order_addres is None:
            order.availability_geo = False

        product_restaurants = []
        order_product_restaurants = []
        for order_item in order.products.all():
            for restaurant_item in order_item.product\
                                             .menu_items\
                                             .filter(availability=True):

                if order.availability_geo:
                    created, lon, lat = location_from_address(
                        location_adress, restaurant_item.restaurant.address)
                    if created:
                        location_adress = GeoLocation.objects.all()

                    restaurant_item.restaurant.distance = round(
                        distance.distance(
                            (lon, lat),
                            (lon_order_addres, lat_order_adress)).km, 3)

                product_restaurants.append(restaurant_item.restaurant)

            order_product_restaurants.append(set(product_restaurants))

        order.access_restaurants = set\
            .intersection(*[set(r) for r in order_product_restaurants])

    return render(
        request,
        template_name='order_items.html',
        context={'orders': orders})
