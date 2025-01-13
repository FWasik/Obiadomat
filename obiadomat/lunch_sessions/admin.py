from django.contrib import admin
from .models import LunchSession, Order, OrderItem


@admin.register(LunchSession)
class LunchSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "restaurant",
        "delivery_time",
        "edit_time",
        "creator",
        "payment_method",
    )
    search_fields = ("name", "restaurant__name", "creator__email")
    list_filter = ("payment_method", "restaurant")
    autocomplete_fields = ("restaurant", "creator", "participants")
    filter_horizontal = ("participants",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "lunch_session", "orderer")
    search_fields = ("orderer__email", "lunch_session__name")
    list_filter = ("lunch_session",)
    autocomplete_fields = ("lunch_session", "orderer")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "meal", "portion")
    search_fields = ("order__orderer__email", "meal__name")
    list_filter = ("meal",)
    autocomplete_fields = ("order", "meal")
