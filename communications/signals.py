from .models import Announcement
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings
from twilio.rest import Client

twilio_account_sid = settings.TWILIO_ACCOUNT_SID
twilio_auth_token = settings.TWILIO_AUTH_TOKEN

twilio_client = Client(twilio_account_sid, twilio_auth_token)


@receiver(post_save, sender=Announcement)
def send_announcement_as_sms(sender, instance, created, **kwargs):
    """
    Sends an announcement as a text message to users.
    """
    if created:
        message = twilio_client.messages.create(
            messaging_service_sid='MG1a63f57041a68c7c2d88222d8d22af67',
            body=instance.text,
            to='+1'
        )
        print(f"Announcement: {instance}")
