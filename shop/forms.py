from django import forms
from .models import NewsletterSubscriber, ProductRating


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


RATING_CHOICES = [(i, f'{i} ★') for i in range(1, 6)]


class RatingForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        choices=RATING_CHOICES,
        coerce=int,
        widget=forms.RadioSelect(attrs={'class': 'star-radio'}),
        label='Оцінка',
    )

    class Meta:
        model = ProductRating
        fields = ['reviewer_name', 'reviewer_email', 'rating', 'comment']
        widgets = {
            'reviewer_name': forms.TextInput(attrs={
                'class': 'form-control',
                "placeholder": "Ваше ім'я",
            }),
            'reviewer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваш email (необов\'язково)',
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Залиште коментар (необов\'язково)',
            }),
        }
        labels = {
            'reviewer_name': "Ім'я",
            'reviewer_email': 'Email',
            'comment': 'Коментар',
        }
