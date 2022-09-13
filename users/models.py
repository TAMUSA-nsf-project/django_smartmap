from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_driver = models.fields.BooleanField(default=0)
    phone = PhoneNumberField(blank=True)

    def __str__(self):
        return self.user.username

# Todo Merge Williams changes with signals
# @receiver(post_save, sender=User)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#         instance.profile.save()


class PreferredRoutes(models.Model):
    user_profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    route_id = models.fields.IntegerField()
