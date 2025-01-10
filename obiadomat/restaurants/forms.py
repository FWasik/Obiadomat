from django import forms
from .models import Restaurant, Meal
from django.core.exceptions import ValidationError


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ("name", "street", "city", "state", "phone_number", "postal_code")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter restaurant name"}),
            "street": forms.TextInput(attrs={"placeholder": "Enter street address"}),
            "city": forms.TextInput(attrs={"placeholder": "Enter city"}),
            "state": forms.TextInput(attrs={"placeholder": "Enter state"}),
            "phone_number": forms.TextInput(
                attrs={"placeholder": "Enter a 9-digit phone number"}
            ),
            "postal_code": forms.TextInput(attrs={"placeholder": "Format: NN-NNN"}),
        }


class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ("name", "price")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter meal name"}),
            "price": forms.NumberInput(
                attrs={"min": "0.01", "step": "0.01", "placeholder": "Enter price"}
            ),
        }
