from django.contrib import admin
from django.urls import path
from .views.home import Index , store
from .views.signup import Signup
from .views.login import Login, logout, forgot, change
from .views.cart import Cart
from .views.checkout import *
from .views.orders import OrderView
from .middlewares.auth import  auth_middleware

urlpatterns = [
    path('', Index.as_view(), name='homepage'),
    path('store', store , name='store'),

    path('signup', Signup.as_view(), name='signup'),
    path('login', Login.as_view(), name='login'),
    path('logout', logout , name='logout'),
    path('forgot', forgot, name='forgot'),
    path('change', change, name='change'),

    path('cart', auth_middleware(Cart.as_view()) , name='cart'),
    path('check-out', CheckOut.as_view() , name='checkout'),
    path('orders', auth_middleware(OrderView.as_view()), name='orders'),
    path('cart/remove/<pk>',Cart.as_view(),name='cart_remove'),
    path('orders/remove/<pk>',OrderView.as_view(),name= 'cart_cancel'),
    path('purchase/<pk>',product_purchase.as_view(),name='purchase'),
    path('purchased/<address>/<phone>/<int:pid>/<int:q>',purchased,name='purchase'),
    path('purchased/<address>/<phone>',purchased,name='purchase'),
    path('payment_success/<pk>',payment_success),
    path('payment_success/<pk>/<flag>',payment_success),
]
