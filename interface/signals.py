from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from profiles import models as profile_models, operations
from stuff import models as stuff_models


@receiver(post_save, sender=User)
def add_profile_pic(user: User, created: bool, *args, **kwargs):
    if created:
        profile_models.Picture(user=user).save()

@receiver(post_save, sender=User)
def assign_full_name(user: User, created: bool, *args, **kwargs):
    if created and (not (user.first_name and user.last_name)):
        user.first_name, user.last_name = stuff_models.Name.get_random_name()
        user.save()
