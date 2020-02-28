from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile,OrderSession

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=User)
def create_order_session(sender, instance, created, **kwargs):
    if created:
        OrderSession.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_order_session(sender, instance, **kwargs):
    instance.ordersession.save()