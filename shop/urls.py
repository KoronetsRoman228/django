from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.main, name='main'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('privacy/', views.privacy, name='privacy'),

    # Кошик
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('cart/checkout/', views.cart_checkout, name='cart_checkout'),

    # Розсилка
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]
