from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from restaurants.models import Restaurant



@receiver(post_save, sender=get_user_model())
def assign_default_group_for_user(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get(name='Customers')
        instance.groups.add(group)
        
        
@receiver(post_migrate)
def create_groups(sender, **kwargs):
    admins, created = Group.objects.get_or_create(name='Admins')
    managers, created = Group.objects.get_or_create(name='Managers')
    Group.objects.get_or_create(name='Customers')
    
    content_type = ContentType.objects.get_for_model(Restaurant)
    permission, created = Permission.objects.get_or_create(
        codename='can_manage_restaurants_in_app',
        name='Can manage restaurants in app',
        content_type=content_type,
    )

    admins.permissions.add(permission)
    managers.permissions.add(permission)