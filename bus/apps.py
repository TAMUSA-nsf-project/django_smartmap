import json
import os

from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate

Stop_Name_KEY = "Stop Name"
std_color_codes = {
    "Route 51": "#9A2A99",
    "Route 51 (reverse)": "#9A2A99",
    "Route 660": "#9A2A99",
    "Route 660 (reverse)": "#9A2A99",
    "Route 672": "#9A2A99",
    "Route 672 (reverse)": "#9A2A99",
}


class BusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bus'

    def ready(self):
        print("Connecting post_migrate signal for predata population.")
        post_migrate.connect(PopulatePreData, sender=self, weak=False)


def addStopIfNotExist(bus_stop: dict):
    from bus.models import BusStop

    if not BusStop.objects.filter(stop_id=bus_stop["Stop Number"]).exists():
        new_stop = BusStop()
        new_stop.name = bus_stop[Stop_Name_KEY]
        new_stop.stop_id = bus_stop["Stop Number"]
        new_stop.latitude = bus_stop["Lat"]
        new_stop.longitude = bus_stop["Lng"]
        new_stop.save()


def addRouteIfNotExist(bus_route: dict):
    from bus.models import BusStop, BusRoute

    busRoute = BusRoute.objects.filter(name=bus_route["name"]).first()
    if busRoute is None:
        print(f'Creating Route {bus_route["name"]} in database.')
        busRoute = BusRoute()
        busRoute.name = bus_route["name"]
        busRoute.first_stop = BusStop.objects.get(stop_id=bus_route["first_stop"])
        busRoute.last_stop = BusStop.objects.get(stop_id=bus_route["last_stop"])
        busRoute.active = True
        busRoute.gmaps_polyline_encoding = busRoute.getGmapsPolylineEncoding()
        if busRoute.name in std_color_codes:
            busRoute.color_code = std_color_codes[busRoute.name]
        busRoute.save()
    elif not busRoute.gmaps_polyline_encoding or not busRoute.gmaps_polyline_bounds:
        print("Adding gmaps polyline data.")
        bus_route_directions_service_result = busRoute.getGmapsDirectionsServiceResult()
        busRoute.gmaps_polyline_encoding = bus_route_directions_service_result.getGmapsPolylineEncoding()
        busRoute.gmaps_polyline_bounds = bus_route_directions_service_result.getGmapsPolylineBounds()
        busRoute.save()
    else:
        print(f'Route {bus_route["name"]} exist in database.')


def addRouteDetailsIfNotExist(bus_stop: dict):
    from bus.models import BusStop, BusRoute, BusRouteDetails

    if not BusRouteDetails.objects.filter(parent_route__name=bus_stop["route"],
                                          bus_stop__stop_id=bus_stop["Stop Number"]).exists():
        new_bus_route_details = BusRouteDetails()
        new_bus_route_details.parent_route = BusRoute.objects.get(name=bus_stop["route"])
        new_bus_route_details.bus_stop = BusStop.objects.get(stop_id=bus_stop["Stop Number"])
        new_bus_route_details.route_index = bus_stop["Order on Route"]
        new_bus_route_details.save()


def PopulatePreData(sender, **kwargs):

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
            addRouteDetailsIfNotExist(bus_stop)
