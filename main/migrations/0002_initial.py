import json
import os

from django.contrib.auth.models import User
from django.db import migrations
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps

import google.auth
from google.cloud import secretmanager
from django.conf import settings
from bus.models import BusStop, BusRoute, BusRouteDetails

Stop_Name_KEY = "Stop Name"


def addStopIfNotExist(bus_stop: dict):
    if not BusStop.objects.filter(stop_id=bus_stop["Stop Number"]).exists():
        new_stop = BusStop()
        new_stop.name = bus_stop[Stop_Name_KEY]
        new_stop.stop_id = bus_stop["Stop Number"]
        new_stop.latitude = bus_stop["Lat"]
        new_stop.longitude = bus_stop["Lng"]
        new_stop.save()


def addRouteIfNotExist(bus_route: dict):
    if not BusRoute.objects.filter(name=bus_route["name"]).exists():
        busRoute = BusRoute()
        busRoute.name = bus_route["name"]
        busRoute.first_stop = BusStop.objects.get(stop_id=bus_route["first_stop"])
        busRoute.last_stop = BusStop.objects.get(stop_id=bus_route["last_stop"])
        busRoute.save()


def addRoteDetailsIfNotExist(bus_stop: dict):
    if not BusRouteDetails.objects.filter(parent_route__name=bus_stop["route"],
                                          bus_stop__stop_id=bus_stop["Stop Number"]).exists():
        new_bus_route_details = BusRouteDetails()
        new_bus_route_details.parent_route = BusRoute.objects.get(name=bus_stop["route"])
        new_bus_route_details.bus_stop = BusStop.objects.get(stop_id=bus_stop["Stop Number"])
        new_bus_route_details.route_index = bus_stop["Order on Route"]
        new_bus_route_details.save()


def populatedata(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    # Read json file with all the route data (bus stops and their lat, lng, etc)
    json_data = None
    with open(os.path.join(settings.BASE_DIR, "route_data/allRoutes.json")) as f:
        json_data = json.load(f)

    # BusStop instances
    for route, bus_stops in json_data.items():
        # Add the first and last stop in this route first
        # First Bus Stop
        addStopIfNotExist(bus_stops[0])
        # Last Bus Stop
        addStopIfNotExist(bus_stops[-1])

        bus_route = {
            "name": route,
            "first_stop": bus_stops[0]["Stop Number"],
            "last_stop": bus_stops[-1]["Stop Number"]
        }
        # Add this route if not already exist
        addRouteIfNotExist(bus_route)

        # Now Add rest of the bus_stops
        for bus_stop in bus_stops:
            addStopIfNotExist(bus_stop)
            addRoteDetailsIfNotExist(bus_stop)


def createsuperuser(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    """
    Dynamically create an admin user as part of a migration
    Password is pulled from Secret Manger.
    """
    if not User.objects.filter(username="admin").exists():

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


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.RunPython(createsuperuser),
                  migrations.RunPython(populatedata)]
