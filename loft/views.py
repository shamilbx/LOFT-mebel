from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import *
from django.views.generic import ListView, DetailView, CreateView
from .forms import LoginForm, RegisterForm, DeliveryForm, EditAccountForm, EditCustomerForm, ContactForm
from django.contrib.auth import login, logout
from django.contrib import messages
# Create your views here.
from .tests import filter_products
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import CartForAuthenticatedUser, cart_info
import stripe
from store.settings import STRIPE_SECRET_KEY


class MainPage(ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'loft/index.html'
    extra_context = {'title': 'LOFT МЕБЕЛЬ КОМФОРТА'}

    def get_queryset(self):
        categories = Category.objects.filter(parent=None)
        return categories


class ProductDetail(DetailView):
    model = Product
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data()
        product = context['product']
        context['title'] = product.title
        context['same_models'] = Product.objects.filter(model=product.model)
        context['same_products'] = Product.objects.filter(category__parent=product.category.parent).exclude(pk=product.pk)

        return context


# Вьюшка для страницы Регистрации и Авторизации
def auth_register_page(request):
    if request.user.is_authenticated:
        return redirect('main')
    else:
        context = {
            'title': 'Авторизация',
            'log_form': LoginForm(),
            'reg_form': RegisterForm()
        }

        return render(request, 'loft/auth.html', context)



def login_user_view(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = LoginForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                if user:
                    login(request, user)
                    return redirect('main')

            messages.error(request, 'не верный логин или пароль')
            return redirect('auth')
    else:
        return redirect('main')


def logout_user_view(request):
    logout(request)
    return redirect('main')


def register_user_view(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = RegisterForm(data=request.POST)
            phone = request.POST.get('phone')
            if form.is_valid():
                user = form.save()
                customer = Customer.objects.create(user=user, phone=phone)
                customer.save()
                cart = Cart.objects.create(customer=customer)
                cart.save()
                login(request, user)
            else:
                for err in form.errors:
                    messages.error(request, form.errors[err].as_text())


        return redirect('auth')
    else:
        return redirect('main')


class ProductByCategory(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'loft/category.html'
    paginate_by = 4

    def get_queryset(self):
        category = Category.objects.get(slug=self.kwargs['slug'])
        products = Product.objects.filter(category__in=category.subcategories.all())
        products = filter_products(self.request, products)
        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductByCategory, self).get_context_data()
        category = Category.objects.get(slug=self.kwargs['slug'])
        context['title'] = category.title
        context['subcats'] = category.subcategories.all()
        context['prices'] = [i for i in range(500, 100001, 500)]
        products = Product.objects.filter(category__slug=self.request.GET.get('cat'))
        context['models'] = set([i.model for i in products])

        return context



# Вьюшка для страницы товаров по акции
class SalesProducts(ListView):
    model = Product
    context_object_name = 'products'
    extra_context = {'title': 'Товары по акции'}
    paginate_by = 2

    def get_queryset(self):
        products = Product.objects.filter(discount__gt=0).order_by('-created_at')
        return products


@login_required(login_url='auth')
def save_favorite_product(request, slug):
    user = request.user
    product = Product.objects.get(slug=slug)
    favorites = FavoriteProduct.objects.filter(user=user)

    if product in [i.product for i in favorites]:
        fav = FavoriteProduct.objects.get(user=user, product=product)
        fav.delete()
    else:
        FavoriteProduct.objects.create(user=user, product=product)

    next_page = request.META.get('HTTP_REFERER', 'main')
    return redirect(next_page)



class FavoriteList(LoginRequiredMixin, ListView):
    model = FavoriteProduct
    context_object_name = 'products'
    template_name = 'loft/product_list.html'
    extra_context = {'title': 'Избранные товары'}
    paginate_by = 4
    login_url = 'auth'

    def get_queryset(self):
        products = FavoriteProduct.objects.filter(user=self.request.user)
        products = [i.product for i in products]
        return products


# Вьюшка для добавления или удаления товраа из корзины
@login_required(login_url='auth')
def add_or_delete_view(request, slug, action):
    user_cart = CartForAuthenticatedUser(request, slug, action)
    next_page = request.META.get('HTTP_REFERER', 'main')
    return redirect(next_page)


@login_required(login_url='auth')
def my_cart_view(request):
    cart = cart_info(request)
    context = {
        'title': 'Корзина',
        'products_cart': cart['products_cart'],
        'cart_price': cart['cart_price'],
        'cart_quantity': cart['cart_quantity']
    }
    return render(request, 'loft/my_cart.html', context)


@login_required(login_url='auth')
def checkout_view(request):
    cart = cart_info(request)
    if cart['products_cart'] and request.method == 'POST':
        regions = Region.objects.all()
        dict_city = {i.pk: [[j.name, j.pk] for j in i.cities.all()] for i in regions}

        context = {
            'products_cart': cart['products_cart'],
            'cart': cart['cart'],
            'title': 'Оформление заказа',
            'form': DeliveryForm(),
            'dict_city': dict_city
        }

        return render(request, 'loft/checkout.html', context)
    else:
        return redirect('main')


@login_required(login_url='auth')
def create_checkout_session(request):
    stripe.api_key = STRIPE_SECRET_KEY
    if request.method == 'POST':
        cart = cart_info(request)
        price = cart['cart_price']

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'rub',
                    'product_data': {'name': ',\n'.join(i.product.title for i in cart['products_cart']) },
                    'unit_amount': int(price) * 100
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('checkout'))
        )

        request.session[f'form_{request.user.pk}'] = request.POST
        return redirect(session.url)



@login_required(login_url='auth')
def success_payment(request):
    cart = cart_info(request)
    try:
        form = request.session.get(f'form_{request.user.pk}')
        request.session.pop(f'form_{request.user.pk}')
    except:
        form = False

    if cart['products_cart'] and form:
        ship_form = DeliveryForm(data=form)
        if ship_form.is_valid():
            delivery = ship_form.save(commit=False)
            delivery.customer = Customer.objects.get(user=request.user)
            delivery.save()

            cart_user = CartForAuthenticatedUser(request)
            cart_user.save_order(delivery)
            cart_user.clear_cart()
        else:
            return redirect('checkout')

        context = {'title': 'Успешная оплата'}
        return render(request, 'loft/success.html', context)

    else:
        return redirect('main')


@login_required(login_url='auth')
def profile_customer_view(request):
    if request.method == 'POST':
        customer_form = EditCustomerForm(request.POST, instance=request.user.customer)
        account_form = EditAccountForm(request.POST, instance=request.user)
        if customer_form.is_valid() and account_form.is_valid():
            customer_form.save()
            account_form.save()
            return redirect('profile')
    else:
        customer_form = EditCustomerForm(instance=request.user.customer)
        account_form = EditAccountForm(instance=request.user)

    order = Order.objects.filter(customer=request.user.customer).last()

    context = {
        'title': f'Профиль {request.user.username}',
        'customer_form': customer_form,
        'account_form': account_form,
        'order': order
    }
    return render(request, 'loft/profile.html', context)



class CustomerOrders(LoginRequiredMixin ,ListView):
    model = Order
    context_object_name = 'orders'
    template_name = 'loft/orders.html'
    extra_context = {'title': 'История заказов'}
    login_url = 'auth'

    def get_queryset(self):
        orders = Order.objects.filter(customer=self.request.user.customer)
        return orders.order_by('-created_at')



class ContactCreateView(CreateView):
    form_class = ContactForm
    model = Contact
    template_name = 'loft/contact.html'
    extra_context = {'title': 'Связаться с нами'}




