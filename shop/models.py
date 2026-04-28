from django.db import models

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
