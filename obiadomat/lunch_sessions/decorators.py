from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from .models import Order, LunchSession
from django.utils import timezone


def creator_or_owner_required(view_func):
    def wrapper(request, *args, **kwargs):
        order = get_object_or_404(Order, id=kwargs.get("order_id"))
        session = get_object_or_404(LunchSession, id=kwargs.get("session_id"))
        user = request.user

        if session.creator != user and order.orderer != user:
            raise PermissionDenied("You are not creator or owner!")

        return view_func(request, *args, **kwargs)

    return wrapper


def creator_or_participation_required(view_func):
    def wrapper(request, *args, **kwargs):
        session = get_object_or_404(LunchSession, id=kwargs.get("session_id"))
        user = request.user

        if user != session.creator and user not in session.participants.all():
            raise PermissionDenied("You are not creator or participant!")

        return view_func(request, *args, **kwargs)

    return wrapper


def time_check_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user
        session = get_object_or_404(LunchSession, id=kwargs.get("session_id"))
        current_time = timezone.localtime(timezone.now())

        if user != session.creator and session.edit_time < current_time:
            raise PermissionDenied("Edit time has passed and you are not creator")

        if session.delivery_time < current_time:
            raise PermissionDenied("Delievery time has passed")

        return view_func(request, *args, **kwargs)

    return wrapper
