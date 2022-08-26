from django.db import models


# Create your models here.


class Announcement(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)
    text = models.TextField(default="")

    def __str__(self):
        return self.text if len(self.text) < 50 else self.text[:50] + "..."
