from django.contrib import admin
from django import forms

from .models import Category, Product, Customer


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category',
            'name',
            'slug',
            'price',
            'stock',
            'description',
            'image',
            'image_url',
            'available',
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Назва товару'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Слаг'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ціна', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Кількість'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Опис товару'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Посилання на зображення (необов\'язково)'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ('name', 'category', 'price', 'stock', 'available', 'created_at', 'updated_at')
    list_filter = ('category', 'available')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Ціна та наявність', {
            'fields': ('price', 'stock', 'available')
        }),
        ('Зображення', {
            'fields': ('image', 'image_url'),
            'description': 'Завантажте фото товару або вкажіть URL.'
        }),
        ('Метадані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'favorite_category', 'created_at', 'updated_at')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('favorite_category',)
