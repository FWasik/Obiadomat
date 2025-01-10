from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    postal_code = models.CharField(
        max_length=6,
        validators=[
            RegexValidator(
                regex=r"^\d{2}-\d{3}$",
                message='Postal code must be in the format NN-NNN (e.g., "12-345").',
            )
        ],
    )
    phone_number = models.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex=r"^\d{9}$", message="Phone number must contain exactly 9 digits."
            )
        ],
    )

    def __str__(self):
        return self.name


class Meal(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, related_name="meals", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )

    def __str__(self):
        return f"{self.name} - {self.price}zł"
