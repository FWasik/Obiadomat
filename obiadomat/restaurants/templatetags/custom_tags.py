from django import template

register = template.Library()


@register.filter
def is_manager_or_admin(user):
    return user.groups.filter(name__in=["Admins", "Managers"]).exists()
