from django.contrib import admin
from .models import Restaurant, Meal


class MealInline(admin.TabularInline):
    model = Meal
    extra = 1
    fields = ("id", "name", "price")


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "street", "city", "phone_number", "creator")
    search_fields = ("name", "street", "city", "phone_number")
    list_filter = ("city", "creator")
    inlines = [MealInline]


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "restaurant")
    search_fields = ("name",)
    list_filter = ("restaurant",)
