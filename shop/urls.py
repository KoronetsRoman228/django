from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.main, name='main'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('page/<int:page_id>/', views.page, name='page'),
]
