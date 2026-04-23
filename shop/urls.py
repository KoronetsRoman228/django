from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.main, name='main'),
    path('page/<int:page_id>/', views.page, name='page'),
]
