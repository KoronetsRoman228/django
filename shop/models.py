from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField('Назва', max_length=100)
    slug = models.SlugField('Слаг', unique=True)
    description = models.TextField('Опис', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категорія'
    )
    name = models.CharField('Назва товару', max_length=150)
    slug = models.SlugField('Слаг', unique=True)
    price = models.DecimalField('Ціна', max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField('Кількість на складі', default=0)
    description = models.TextField('Опис товару', blank=True)
    image_url = models.URLField('Фото URL', blank=True)
    image = models.ImageField('Фото товару', upload_to='products/', blank=True, null=True)
    available = models.BooleanField('В наявності', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'

    def __str__(self):
        return self.name


class Customer(models.Model):
    first_name = models.CharField('Ім’я', max_length=80)
    last_name = models.CharField('Прізвище', max_length=80)
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    favorite_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='favorite_customers',
        verbose_name='Улюблена категорія'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = 'Покупець'
        verbose_name_plural = 'Покупці'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


# ─── Кошик ────────────────────────────────────────────────────────────────────

class Order(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Користувач')
    session_key = models.CharField('Ключ сесії', max_length=40)
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    is_completed = models.BooleanField('Завершено', default=False)

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'

    def __str__(self):
        return f'Замовлення #{self.pk}'

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Замовлення')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField('Кількість', default=1)
    price = models.DecimalField('Ціна', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Позиція замовлення'
        verbose_name_plural = 'Позиції замовлення'

    def __str__(self):
        return f'{self.product.name} x{self.quantity}'

    def get_subtotal(self):
        return self.price * self.quantity


# ─── Підписка на розсилку ─────────────────────────────────────────────────────

class NewsletterSubscriber(models.Model):
    name = models.CharField('Імʼя', max_length=100)
    email = models.EmailField('Email', unique=True)
    subscribed_at = models.DateTimeField('Дата підписки', auto_now_add=True)
    is_active = models.BooleanField('Активна підписка', default=True)

    class Meta:
        verbose_name = 'Підписник розсилки'
        verbose_name_plural = 'Підписники розсилки'

    def __str__(self):
        return f'{self.name} <{self.email}>'


# ─── Оцінка товару ────────────────────────────────────────────────────────────

class ProductRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings', verbose_name='Товар')
    reviewer_name = models.CharField('Імʼя', max_length=100)
    reviewer_email = models.EmailField('Email', blank=True)
    rating = models.PositiveSmallIntegerField(
        'Оцінка',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField('Коментар', blank=True)
    created_at = models.DateTimeField('Дата оцінки', auto_now_add=True)

    class Meta:
        verbose_name = 'Оцінка товару'
        verbose_name_plural = 'Оцінки товарів'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.product.name} — {self.rating}★ від {self.reviewer_name}'


# ─── Кампанія розсилки ────────────────────────────────────────────────────────

class NewsletterCampaign(models.Model):
    subject = models.CharField('Тема листа', max_length=200)
    body_html = models.TextField('Тіло листа (HTML)')
    body_text = models.TextField('Тіло листа (текст)', blank=True,
                                  help_text='Текстова версія для клієнтів без HTML. Заповнюється автоматично якщо порожньо.')
    sent_at = models.DateTimeField('Дата відправки', null=True, blank=True)
    recipients_count = models.PositiveIntegerField('Кількість отримувачів', default=0)
    is_sent = models.BooleanField('Відправлено', default=False)
    created_at = models.DateTimeField('Створено', auto_now_add=True)

    class Meta:
        verbose_name = 'Кампанія розсилки'
        verbose_name_plural = 'Кампанії розсилки'
        ordering = ['-created_at']

    def __str__(self):
        status = '✅ Надіслано' if self.is_sent else '📝 Чернетка'
        return f'{self.subject} [{status}]'
