from .models import Announcement
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings
from twilio.rest import Client

from users.models import Profile

# Get Twilio env variables
twilio_account_sid = settings.TWILIO_ACCOUNT_SID
twilio_auth_token = settings.TWILIO_AUTH_TOKEN

# Create a Twilio client
twilio_client = Client(twilio_account_sid, twilio_auth_token)


@receiver(post_save, sender=Announcement)
def send_announcement_as_sms(sender, instance, created, **kwargs):
    """
    Sends an announcement as a text message to users.
    """
    if created:
        # Get profiles with a phone number (exclude those without)
        profiles_with_phone = Profile.objects.exclude(phone="")

        # TODO is the following blocking, do we need to setup async task-scheduling? Possibly use Django Q
        for profile in profiles_with_phone:
            message = twilio_client.messages.create(
                messaging_service_sid='MG1a63f57041a68c7c2d88222d8d22af67',
                body=instance.text,
                to=str(profile.phone)
            )

        if settings.DEBUG and profiles_with_phone:
            print(f"announcement sent via SMS: '{instance}'")
