from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from .models import Restaurant, Meal
from .decorators import creator_required
from django.contrib.auth.decorators import permission_required
from .forms import RestaurantForm, MealForm
from .mixins import CreatorRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError


class RestaurantCreateView(
    SuccessMessageMixin, PermissionRequiredMixin, LoginRequiredMixin, CreateView
):
    model = Restaurant
    form_class = RestaurantForm
    template_name = "restaurant_form.html"
    success_url = reverse_lazy("restaurants:restaurant_list")
    success_message = "You successfully created a restaurant!"
    permission_required = "restaurants.can_manage_restaurants_in_app"

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class RestaurantListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Restaurant
    template_name = "restaurant_list.html"
    context_object_name = "restaurants"
    permission_required = "restaurants.can_manage_restaurants_in_app"

    def get_queryset(self):
        return Restaurant.objects.filter(creator=self.request.user).order_by("id")


class RestaurantUpdateView(
    SuccessMessageMixin,
    CreatorRequiredMixin,
    PermissionRequiredMixin,
    LoginRequiredMixin,
    UpdateView,
):
    model = Restaurant
    form_class = RestaurantForm
    template_name = "restaurant_form.html"
    success_url = reverse_lazy("restaurants:restaurant_list")
    success_message = "You successfully updated a restaurant!"
    permission_required = "restaurants.can_manage_restaurants_in_app"


class RestaurantDeleteView(
    SuccessMessageMixin,
    CreatorRequiredMixin,
    PermissionRequiredMixin,
    LoginRequiredMixin,
    DeleteView,
):
    model = Restaurant
    template_name = "restaurant_confirm_delete.html"
    success_url = reverse_lazy("restaurants:restaurant_list")
    success_message = "You successfully deleted a restaurant!"
    permission_required = "restaurants.can_manage_restaurants_in_app"


@login_required
@creator_required
@permission_required("restaurants.can_manage_restaurants_in_app", raise_exception=True)
def restaurant_meals_view(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == "POST":
        meal_form = MealForm(request.POST)
        if meal_form.is_valid():
            meal = meal_form.save(commit=False)
            meal.restaurant = restaurant
            meal.save()

            messages.success(request, "You successfully added meal!")
            #return redirect("restaurants:restaurant_meals", restaurant_id=restaurant.id)

    meal_form = MealForm()
    meals = restaurant.meals.all()

    return render(
        request,
        "restaurant_meals.html",
        {
            "meal_form": meal_form,
            "restaurant": restaurant,
            "meals": meals,
        },
    )


@login_required
@creator_required
@permission_required("restaurants.can_manage_restaurants_in_app", raise_exception=True)
def update_meal_view(request, restaurant_id, meal_id):
    new_name = request.POST.get("name")
    new_price = request.POST.get("price")
    
    try:
        if not new_name or not new_price:
            raise ValidationError("Fields cannot be empty!")
        
        meal = get_object_or_404(Meal, id=meal_id)

        meal.name = new_name
        meal.price = new_price
        meal.save()
        
        messages.success(request, "You successfully updated meal!")
        
    except Exception as e:
        messages.error(request, e.message)
        
    return redirect("restaurants:restaurant_meals", restaurant_id=restaurant_id)


@login_required
@creator_required
@permission_required("restaurants.can_manage_restaurants_in_app", raise_exception=True)
def delete_meal_view(request, restaurant_id, meal_id):
    try:
        meal = get_object_or_404(Meal, id=meal_id)
        meal.delete()

        messages.success(request, "You successfully deleted meal!")
        
    except Exception as e:
        messages.error(request, e.message)

    return redirect("restaurants:restaurant_meals", restaurant_id=restaurant_id)
