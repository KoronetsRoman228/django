from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Category, Product


def main(request):
    categories = Category.objects.all()
    products_list = Product.objects.filter(available=True).select_related('category')
    paginator = Paginator(products_list, 6)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'products': products,
        'is_paginated': products.has_other_pages(),
        'page_obj': products,
        'paginator': paginator,
    }
    return render(request, 'shop/main.html', context)


def category(request, slug):
    categories = Category.objects.all()
    category_obj = get_object_or_404(Category, slug=slug)
    products_list = category_obj.products.filter(available=True)
    paginator = Paginator(products_list, 6)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'category': category_obj,
        'products': products,
        'is_paginated': products.has_other_pages(),
        'page_obj': products,
        'paginator': paginator,
    }
    return render(request, 'shop/category.html', context)


def product_detail(request, slug):
    categories = Category.objects.all()
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(
        category=product.category, available=True
    ).exclude(pk=product.pk)[:4]
    context = {
        'categories': categories,
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'shop/product_detail.html', context)


def about(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'title': 'Про нас',
    }
    return render(request, 'shop/about.html', context)


def contacts(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'title': 'Контакти',
    }
    return render(request, 'shop/contacts.html', context)


def privacy(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'title': 'Політика конфіденційності',
    }
    return render(request, 'shop/privacy.html', context)
