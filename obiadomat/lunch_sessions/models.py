from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from datetime import timedelta
from django.utils import timezone
from restaurants.models import Restaurant, Meal

User = get_user_model()


def get_default_delivery_time():
    return timezone.localtime(timezone.now()) + timedelta(hours=3)


def get_default_edit_time():
    return timezone.localtime(timezone.now()) + timedelta(hours=1)


class LunchSession(models.Model):
    CASH = "cash"
    CARD = "card"

    PAYMENT_METHOD_CHOICES = [
        (CASH, "Cash"),
        (CARD, "Card"),
    ]

    name = models.CharField(max_length=255)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    delivery_time = models.DateTimeField(default=get_default_delivery_time)
    edit_time = models.DateTimeField(default=get_default_edit_time)
    creator = models.ForeignKey(
        User, related_name="created_sessions", on_delete=models.CASCADE
    )
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    participants = models.ManyToManyField(
        User, related_name="participated_sessions", blank=True
    )

    class Meta:
        ordering = ["edit_time"]

    def save(self, *args, **kwargs):
        if self.pk:
            session = LunchSession.objects.get(pk=self.pk)

            if session.restaurant != self.restaurant:
                self.orders.all().delete()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Order(models.Model):
    lunch_session = models.ForeignKey(
        LunchSession, related_name="orders", on_delete=models.CASCADE
    )
    orderer = models.ForeignKey(User, related_name="user_orders", on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("lunch_session", "orderer")


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="order_items", on_delete=models.CASCADE
    )
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    portion = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
