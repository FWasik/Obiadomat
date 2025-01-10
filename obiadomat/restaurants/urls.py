from django.urls import path
from . import views

app_name = "restaurants"

urlpatterns = [
    path("", views.RestaurantListView.as_view(), name="restaurant_list"),
    path("create/", views.RestaurantCreateView.as_view(), name="restaurant_create"),
    path(
        "update/<int:pk>/",
        views.RestaurantUpdateView.as_view(),
        name="restaurant_update",
    ),
    path(
        "delete/<int:pk>/",
        views.RestaurantDeleteView.as_view(),
        name="restaurant_delete",
    ),
    path("<int:restaurant_id>/meals/", views.restaurant_meals_view, name="restaurant_meals"),
    path(
        "<int:restaurant_id>/meals/update/<int:meal_id>/",
        views.update_meal_view,
        name="update_meal",
    ),
    path(
        "<int:restaurant_id>/meals/delete/<int:meal_id>/",
        views.delete_meal_view,
        name="delete_meal",
    ),
]
