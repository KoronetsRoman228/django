from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Avg
from .models import Category, Product, Order, OrderItem, NewsletterSubscriber, ProductRating
from .forms import NewsletterForm, RatingForm, RegisterForm


def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    user = request.user if request.user.is_authenticated else None
    order, _ = Order.objects.get_or_create(
        session_key=session_key, user=user, is_completed=False
    )
    return order


def main(request):
    categories = Category.objects.all()
    products_list = Product.objects.filter(available=True).select_related('category')
    paginator = Paginator(products_list, 6)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    newsletter_form = NewsletterForm()

    context = {
        'categories': categories,
        'products': products,
        'is_paginated': products.has_other_pages(),
        'page_obj': products,
        'paginator': paginator,
        'newsletter_form': newsletter_form,
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

    ratings = product.ratings.all().order_by('-created_at')
    avg_rating = ratings.aggregate(avg=Avg('rating'))['avg']

    rating_form = None
    if request.user.is_authenticated:
        rating_form = RatingForm()
        if request.method == 'POST' and 'submit_rating' in request.POST:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                r = rating_form.save(commit=False)
                r.product = product
                r.reviewer_name = request.user.username
                r.reviewer_email = request.user.email
                r.save()
                messages.success(request, 'Дякуємо за вашу оцінку!')
                return redirect('shop:product_detail', slug=slug)
            else:
                messages.error(request, 'Будь ласка, виправте помилки у формі оцінки.')

    context = {
        'categories': categories,
        'product': product,
        'related_products': related_products,
        'ratings': ratings,
        'avg_rating': avg_rating,
        'rating_form': rating_form,
    }
    return render(request, 'shop/product_detail.html', context)


def about(request):
    categories = Category.objects.all()
    return render(request, 'shop/about.html', {'categories': categories, 'title': 'Про нас'})


def contacts(request):
    categories = Category.objects.all()
    newsletter_form = NewsletterForm()
    return render(request, 'shop/contacts.html', {
        'categories': categories,
        'title': 'Контакти',
        'newsletter_form': newsletter_form,
    })


def privacy(request):
    categories = Category.objects.all()
    return render(request, 'shop/privacy.html', {'categories': categories, 'title': 'Політика конфіденційності'})


# ── Кошик ─────────────────────────────────────────────────────────────────────

def cart(request):
    categories = Category.objects.all()
    order = get_or_create_cart(request)
    return render(request, 'shop/cart.html', {'categories': categories, 'order': order})


def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    order = get_or_create_cart(request)
    item, created = OrderItem.objects.get_or_create(
        order=order, product=product,
        defaults={'price': product.price, 'quantity': 1}
    )
    if not created:
        item.quantity += 1
        item.save()
    messages.success(request, f'«{product.name}» додано до кошика!')
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER', '/')
    return redirect(next_url)


def cart_remove(request, item_id):
    item = get_object_or_404(OrderItem, pk=item_id)
    item.delete()
    messages.success(request, 'Товар видалено з кошика.')
    return redirect('shop:cart')


def cart_update(request, item_id):
    item = get_object_or_404(OrderItem, pk=item_id)
    qty = int(request.POST.get('quantity', 1))
    if qty < 1:
        item.delete()
    else:
        item.quantity = qty
        item.save()
    return redirect('shop:cart')


def cart_checkout(request):
    order = get_or_create_cart(request)
    if order.items.count() == 0:
        messages.error(request, 'Кошик порожній!')
        return redirect('shop:cart')
    if request.user.is_authenticated:
        order.user = request.user
    order.is_completed = True
    order.save()
    messages.success(request, 'Замовлення успішно оформлено! Дякуємо за покупку!')
    return redirect('shop:main')


# ── Розсилка ──────────────────────────────────────────────────────────────────

def newsletter_subscribe(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if NewsletterSubscriber.objects.filter(email=email).exists():
                messages.info(request, 'Ця адреса вже підписана на розсилку.')
            else:
                subscriber = form.save()
                # Надсилаємо лист-привітання
                from .email_service import send_welcome_email
                send_welcome_email(subscriber)
                messages.success(request, f'Дякуємо, {subscriber.name}! Ви підписались на розсилку. Перевірте свою пошту — ми надіслали вітальний лист.')
        else:
            messages.error(request, 'Перевірте введені дані.')
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER', '/')
    return redirect(next_url)


# ── Аутентифікація ────────────────────────────────────────────────────────────

def register(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Вітаємо, {user.username}! Ви успішно зареєструвались.')
            return redirect('shop:main')
    else:
        form = RegisterForm()
    return render(request, 'shop/register.html', {
        'categories': categories,
        'form': form,
        'title': 'Реєстрація',
    })


@login_required
def profile(request):
    categories = Category.objects.all()
    if request.user.is_superuser:
        orders = Order.objects.filter(is_completed=True).order_by('-created_at')
    else:
        orders = Order.objects.filter(user=request.user, is_completed=True).order_by('-created_at')
    return render(request, 'shop/profile.html', {
        'categories': categories,
        'orders': orders,
        'title': 'Особистий кабінет',
    })
