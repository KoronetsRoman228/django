from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import NewsletterSubscriber, ProductRating, Customer


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(
        required=True,
        max_length=20,
        label='Телефон',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Користувач з таким email вже існує.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Customer.objects.update_or_create(
                email=user.email,
                defaults={
                    'phone': self.cleaned_data['phone'],
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                }
            )
        return user


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Ваше ім'я",
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваш email',
            }),
        }
        labels = {
            'name': "Ім'я",
            'email': 'Email',
        }


RATING_CHOICES = [(i, f'{i} ★') for i in range(5, 0, -1)]


class RatingForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        choices=RATING_CHOICES,
        coerce=int,
        widget=forms.RadioSelect(attrs={'class': 'star-radio'}),
        label='Оцінка',
    )

    class Meta:
        model = ProductRating
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Залиште коментар (необов\'язково)',
            }),
        }
        labels = {
            'comment': 'Коментар',
        }
