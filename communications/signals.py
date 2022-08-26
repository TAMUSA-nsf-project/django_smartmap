
from .models import Announcement
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Announcement)
def send_announcement_as_sms(sender, instance, created, **kwargs):
    """
    Sends an announcement as a text message to users.
    """
    if created:
        print("A NEW ANNOUNCEMENT WAS CREATED!!!")