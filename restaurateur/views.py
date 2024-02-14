from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from foodcartapp.models import (MakeOrder, Product, Restaurant,
                                RestaurantMenuItem)


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


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    restaurant_objects = Restaurant.objects.all()
    restaurant_names = {
        restaurant.id: restaurant.name for restaurant in restaurant_objects}
    restaurant_addresses = {
        restaurant.id: restaurant.address for restaurant in restaurant_objects}

    restaurant_menu_items = (
        RestaurantMenuItem.objects
        .select_related('restaurant', 'product')
        .filter(availability=True)
        .order_by('product'))

    restaurant_menu_items_ids = {}
    for menu_item in restaurant_menu_items:
        restaurant_menu_items_ids.setdefault(menu_item.restaurant.id, [])
        restaurant_menu_items_ids[menu_item.restaurant.id].append(
            menu_item.product_id)

    order_items = []
    orders = (
        MakeOrder.objects.all()
        .with_amount()
        .order_by('-status', 'id')
        .prefetch_related('products')
        .exclude(status=MakeOrder.ChoicesStatus.COMPLETED))

    for order in orders:
        order_products = [
            order_product.product.id
            for order_product
            in order.products.all().select_related('product')]

        cooks_restaurants = []
        for restaurant_id in restaurant_menu_items_ids.keys():
            if set(order_products).issubset(restaurant_menu_items_ids[restaurant_id]):
                cooks_restaurants.append(restaurant_id)

        order_items.append({
            'id': order.id,
            'status': order.get_status_display(),
            'payment_method': order.get_payment_method_display(),
            'amount': order.amount,
            'full_name': order.full_name,
            'contact_phone': order.contact_phone,
            'address': order.address,
            'comment': order.comment,
            'restaurants': cooks_restaurants,
            'cook_restaurant': order.cook_restaurant
        })
    return render(
        request,
        template_name='order_items.html',
        context={
            'order_items': order_items,
            'restaurant_names': restaurant_names
        })
