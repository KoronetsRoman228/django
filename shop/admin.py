from django.contrib import admin, messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import path
from django import forms

from .models import (Category, Product, Customer,
                     Order, OrderItem,
                     NewsletterSubscriber, NewsletterCampaign,
                     ProductRating)


# ─── Product ──────────────────────────────────────────────────────────────────

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'price', 'stock', 'description',
                  'image', 'image_url', 'available']
        widgets = {
            'category':    forms.Select(attrs={'class': 'form-control'}),
            'name':        forms.TextInput(attrs={'class': 'form-control'}),
            'slug':        forms.TextInput(attrs={'class': 'form-control'}),
            'price':       forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock':       forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image':       forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'image_url':   forms.URLInput(attrs={'class': 'form-control'}),
            'available':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'favorite_category', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('favorite_category',)


# ─── Order ────────────────────────────────────────────────────────────────────

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'session_key', 'get_total', 'get_total_items', 'is_completed', 'created_at')
    list_filter = ('is_completed',)
    inlines = [OrderItemInline]


# ─── Newsletter ───────────────────────────────────────────────────────────────

class SendCampaignForm(forms.Form):
    """Форма для підтвердження відправки кампанії."""
    confirm = forms.BooleanField(
        label='Я підтверджую відправку листа всім активним підписникам',
        required=True
    )


class CampaignAdminForm(forms.ModelForm):
    """Форма редагування кампанії з WYSIWYG-підказкою."""
    class Meta:
        model = NewsletterCampaign
        fields = ['subject', 'body_html', 'body_text']
        widgets = {
            'subject': forms.TextInput(attrs={
                'style': 'width:100%',
                'placeholder': 'Наприклад: 🌵 Нові кактуси вже в магазині!'
            }),
            'body_html': forms.Textarea(attrs={
                'rows': 20,
                'style': 'width:100%; font-family:monospace',
                'placeholder': (
                    'HTML-тіло листа. Можна використовувати теги:\n'
                    '<h2>Заголовок</h2>\n'
                    '<p>Абзац тексту</p>\n'
                    '<ul><li>Пункт 1</li></ul>\n'
                    '<a href="http://...">Посилання</a>\n\n'
                    'Приклад з акцією:\n'
                    '<h2>🏷️ Знижка 20% на всі кактуси!</h2>\n'
                    '<p>Тільки цього тижня отримайте знижку на весь асортимент.</p>'
                ),
            }),
            'body_text': forms.Textarea(attrs={
                'rows': 8,
                'style': 'width:100%',
                'placeholder': 'Текстова версія (необов\'язково — заповниться автоматично)',
            }),
        }


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_active', 'subscribed_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'email')
    actions = ['mark_active', 'mark_inactive']

    @admin.action(description='✅ Позначити як активні')
    def mark_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='❌ Позначити як неактивні')
    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    form = CampaignAdminForm
    list_display = ('subject', 'is_sent', 'recipients_count', 'sent_at', 'created_at')
    list_filter = ('is_sent',)
    readonly_fields = ('is_sent', 'sent_at', 'recipients_count', 'created_at')

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                '<int:campaign_id>/send/',
                self.admin_site.admin_view(self.send_campaign_view),
                name='shop_newslettercampaign_send',
            ),
        ]
        return custom + urls

    def send_campaign_view(self, request, campaign_id):
        """Кастомна сторінка підтвердження і відправки кампанії."""
        from .email_service import send_campaign

        campaign = get_object_or_404(NewsletterCampaign, pk=campaign_id)
        active_count = NewsletterSubscriber.objects.filter(is_active=True).count()

        if campaign.is_sent:
            self.message_user(request, 'Цю кампанію вже було надіслано!', level=messages.WARNING)
            return redirect('admin:shop_newslettercampaign_changelist')

        if request.method == 'POST':
            form = SendCampaignForm(request.POST)
            if form.is_valid():
                try:
                    sent = send_campaign(campaign)
                    self.message_user(
                        request,
                        f'✅ Кампанію «{campaign.subject}» надіслано {sent} підписникам!',
                        level=messages.SUCCESS,
                    )
                except Exception as exc:
                    self.message_user(request, f'❌ Помилка: {exc}', level=messages.ERROR)
                return redirect('admin:shop_newslettercampaign_changelist')
        else:
            form = SendCampaignForm()

        context = {
            **self.admin_site.each_context(request),
            'campaign': campaign,
            'active_count': active_count,
            'form': form,
            'title': f'Надіслати кампанію: {campaign.subject}',
            'opts': self.model._meta,
        }
        return render(request, 'admin/shop/send_campaign.html', context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_send_button'] = True
        return super().change_view(request, object_id, form_url, extra_context)


# ─── Rating ───────────────────────────────────────────────────────────────────

@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ('product', 'reviewer_name', 'rating', 'created_at')
    list_filter = ('rating', 'product')
    search_fields = ('reviewer_name', 'product__name')


# ─── Custom User Admin ────────────────────────────────────────────────────────

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    def has_add_permission(self, request):
        return False

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
