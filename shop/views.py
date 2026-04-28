from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Category, Product


def get_pages():
    return [
        {'id': 1, 'name': 'Сторінка 1', 'path': '/page/1/'},
        {'id': 2, 'name': 'Сторінка 2', 'path': '/page/2/'},
        {'id': 3, 'name': 'Сторінка 3', 'path': '/page/3/'},
    ]


def main(request):
    categories = Category.objects.all()
    products_list = Product.objects.filter(available=True)
    paginator = Paginator(products_list, 6)  # 6 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'pages': get_pages(),
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
        'pages': get_pages(),
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
    context = {
        'categories': categories,
        'product': product,
    }
    return render(request, 'shop/product_detail.html', context)


def about(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'title': 'Про нас',
        'message': 'Це магазин кактусів з чудовою колекцією рідкісних та класичних кактусів.',
    }
    return render(request, 'shop/about.html', context)


def contacts(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'title': 'Контакти',
        'message': 'Телефон: +380 67 123 45 67\nEmail: info@cactus-shop.ua',
    }
    return render(request, 'shop/contacts.html', context)


def privacy(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'title': 'Політика конфіденційності',
        'message': 'Ми поважаємо вашу приватність і не передаємо дані третім особам.',
    }
    return render(request, 'shop/privacy.html', context)


def page(request, page_id):
    categories = Category.objects.all()
    page_title = f'Сторінка {page_id}'
    context = {
        'title': page_title,
        'message': f'Ви зараз на {page_title}. Натисніть, щоб повернутися на головну.',
        'categories': categories,
        'pages': get_pages(),
        'is_main': False,
    }
    return render(request, 'shop/page.html', context)
