from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class BusDriver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ("access_busdriver_pages", "Can access bus driver pages.")
        ]

    def __str__(self):
        return self.user.username