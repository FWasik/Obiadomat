from .models import LunchSession
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from restaurants.models import Meal
from .models import Order, OrderItem

User = get_user_model()


class LunchSessionForm(forms.ModelForm):
    # participants = forms.ModelMultipleChoiceField(
    #     queryset=User.objects.all(), required=False
    # )

    class Meta:
        model = LunchSession
        fields = (
            "name",
            "restaurant",
            "payment_method",
            "edit_time",
            "delivery_time",
            "participants",
        )
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter lunch session name"}),
            "delivery_time": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "placeholder": "Select delivery time",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "edit_time": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "placeholder": "Select edit time",
                },
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        delivery_time = cleaned_data.get("delivery_time")
        edit_time = cleaned_data.get("edit_time")

        if edit_time and delivery_time and edit_time > delivery_time:
            raise ValidationError("Edit time cannot be greater than delivery time.")

        return cleaned_data


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class OrderItemForm(forms.ModelForm):
    portion = forms.IntegerField(min_value=1)

    class Meta:
        model = OrderItem
        fields = ["meal", "portion"]

    def __init__(self, *args, **kwargs):
        lunch_session = kwargs.pop("session", None)
        super().__init__(*args, **kwargs)

        if lunch_session and lunch_session.restaurant:
            self.fields["meal"].queryset = Meal.objects.filter(
                restaurant=lunch_session.restaurant
            )


OrderItemFormSet = forms.inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
    can_delete_extra=False,
)
