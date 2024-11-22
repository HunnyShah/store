from django import forms
from .models import Product, CartItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description']

class UpdateQuantityForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1, 'class': 'w-16 text-center'})
        }