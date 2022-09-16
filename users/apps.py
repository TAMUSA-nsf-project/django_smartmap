import os

import google
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        # print("Connecting post_migrate signal for superuser creation.")
        post_migrate.connect(CreateSuperUserIfNotExist, sender=self, weak=False)
        import users.signals


def CreateSuperUserIfNotExist(sender, **kwargs):
    from google.cloud import secretmanager
    from django.contrib.auth.models import User

    """
    Dynamically create an admin user as part of a migration
    Password is pulled from Secret Manger.
    """
    if not User.objects.filter(username="admin").exists():
        print("Creating Superuser admin.")
        if os.getenv("GOOGLE_CLOUD_PROJECT", None) is None:
            # We are in DEV
            admin_password = "P@ssword1"
        else:
            client = secretmanager.SecretManagerServiceClient()

            # Get project value for identifying current context
            _, project = google.auth.default()

            # Retrieve the previously stored admin password
            PASSWORD_NAME = os.environ.get("PASSWORD_NAME", "superuser_password")
            name = f"projects/{project}/secrets/{PASSWORD_NAME}/versions/latest"
            admin_password = client.access_secret_version(name=name).payload.data.decode(
                "UTF-8"
            )

        # Create a new user using acquired password, stripping any accidentally stored newline characters
        User.objects.create_superuser("admin", password=admin_password.strip())
    else:
        print("admin user exist.")
