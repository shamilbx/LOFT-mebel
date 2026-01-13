from django.urls import path
from .views import *

urlpatterns = [
    path('', MainPage.as_view(), name='main'),
    path('product/<slug:slug>/', ProductDetail.as_view(), name='detail'),
    path('authentication/', auth_register_page, name='auth'),
    path('login/', login_user_view, name='login'),
    path('logout/', logout_user_view, name='logout'),
    path('register/', register_user_view, name='register'),
    path('category/<slug:slug>/', ProductByCategory.as_view(), name='category'),
    path('sales/', SalesProducts.as_view(), name='sales'),
    path('action_favorite/<slug:slug>/', save_favorite_product, name='action_fav'),
    path('favorites/', FavoriteList.as_view(), name='favs'),
    path('action_cart/<slug:slug>/<str:action>/', add_or_delete_view, name='action_cart'),
    path('basket/', my_cart_view, name='basket'),
    path('checkout/', checkout_view, name='checkout'),
    path('payment/', create_checkout_session, name='payment'),
    path('success/', success_payment, name='success'),
    path('profile/', profile_customer_view, name='profile'),
    path('orders/', CustomerOrders.as_view(), name='orders'),
    path('contact/', ContactCreateView.as_view(), name='contact'),
]
