from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User


# https: // stackoverflow.com/questions/61656796/how-do-i-set-a-user-as -inactive-in -django-when-registering
@receiver(post_save, sender=User)
def user_to_inactive(sender, instance, created, update_fields, **kwargs):
    if created:
        instance.is_active = False
