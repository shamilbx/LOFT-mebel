from django import forms
from .models import Category, Delivery, Customer, Contact
from django_svg_image_form_field import SvgAndImageFormField
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = []
        field_classes = {
            'icon': SvgAndImageFormField,
        }


# Форма Авторизации
class LoginForm(AuthenticationForm):
    username = forms.EmailField(label=False, widget=forms.EmailInput(attrs={
        'class': 'contact__section-input'
    }))

    password = forms.CharField(label=False, widget=forms.PasswordInput(attrs={
        'class': 'contact__section-input'
    }))


class RegisterForm(UserCreationForm):
    username = forms.EmailField(label=False, widget=forms.EmailInput(attrs={
        'class': 'contact__section-input'
    }))

    password1 = forms.CharField(label=False, widget=forms.PasswordInput(attrs={
        'class': 'contact__section-input'
    }))

    password2 = forms.CharField(label=False, widget=forms.PasswordInput(attrs={
        'class': 'contact__section-input'
    }))

    first_name = forms.CharField(label=False, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    last_name = forms.CharField(label=False, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name')



class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ('region', 'city', 'street', 'home', 'flat', 'comment', 'phone')
        widgets = {
            'region': forms.Select(attrs={'class': 'contact__section-input'}),
            'city': forms.Select(attrs={'class': 'contact__section-input'}),
            'street': forms.TextInput(attrs={'class': 'contact__section-input'}),
            'home': forms.TextInput(attrs={'class': 'contact__section-input'}),
            'flat': forms.TextInput(attrs={'class': 'contact__section-input'}),
            'comment': forms.Textarea(attrs={'class': 'contact__section-input'}),
            'phone': forms.TelInput(attrs={'class': 'contact__section-input'})
        }



class EditAccountForm(forms.ModelForm):
    username = forms.EmailField(label=False, widget=forms.EmailInput(attrs={
        'class': 'contact__section-input'
    }))

    first_name = forms.CharField(label=False, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    last_name = forms.CharField(label=False, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class EditCustomerForm(forms.ModelForm):
    phone = forms.CharField(widget=forms.TelInput(attrs={
        'class': 'contact__section-input'
    }))

    region = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    street = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    house = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    flat = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    class Meta:
        model = Customer
        fields = ('phone', 'region', 'city', 'street', 'house', 'flat')




class ContactForm(forms.ModelForm):
    full_name = forms.CharField(label=False, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    phone = forms.CharField(label=False, widget=forms.TelInput(attrs={
        'class': 'contact__section-input'
    }))

    text = forms.CharField(label=False, widget=forms.Textarea(attrs={
        'class': 'contact__section-input'
    }))

    photo = forms.FileField(label='Файл или Фото', widget=forms.FileInput(attrs={
        'class': 'contact__section-input mx-3'
    }))

    class Meta:
        model = Contact
        fields = ('full_name', 'phone', 'text', 'photo')


















