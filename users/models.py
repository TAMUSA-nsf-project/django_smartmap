from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_driver = models.fields.BooleanField()
    phone = models.fields.CharField(max_length=17)

    def __str__(self):
        return self.user.username


def create_profile(sender, **kwargs):
    if kwargs['created']:
        profile = Profile.objects.create(user=kwargs['instance'])


class PreferredRoutes(models.Model):
    user_profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    route_id = models.fields.IntegerField()


post_save.connect(create_profile, sender=User)
