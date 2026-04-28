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
    path('page/<int:page_id>/', views.page, name='page'),
]
