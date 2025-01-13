from django import template
from django.db.models import Sum, F, DecimalField

register = template.Library()


@register.filter
def user_total_session_cost(user, session):
    user_order = session.orders.filter(orderer=user).first()

    if not user_order:
        return 0

    user_total_session_cost = (
        sum(item.meal.price * item.portion for item in user_order.order_items.all())
        or 0
    )

    return user_total_session_cost
