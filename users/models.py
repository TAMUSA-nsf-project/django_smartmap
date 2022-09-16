from django.contrib.auth.models import User
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_driver = models.fields.BooleanField(default=0)
    phone = PhoneNumberField(blank=True)

    def __str__(self):
        return self.user.username


class PreferredRoutes(models.Model):
    user_profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    route_id = models.fields.IntegerField()
