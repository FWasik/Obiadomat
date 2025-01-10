from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from .models import Restaurant


def creator_required(view_func):
    def wrapper(request, *args, **kwargs):
        restaurant = get_object_or_404(Restaurant, id=kwargs.get("restaurant_id"))
        if restaurant.creator != request.user:
            raise PermissionDenied("You are not creator of a restaurant!")

        return view_func(request, *args, **kwargs)

    return wrapper
