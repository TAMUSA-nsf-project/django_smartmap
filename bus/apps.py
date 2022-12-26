import datetime
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
    "Route 64": "#f28120",
    "Route 64 (reverse)": "#f28120",
    "Route 30": "#913493",
    "Route 30 (reverse)": "#913493",
    "Route 100": "#363C74",
    "Route 100 (reverse)": "#363C74",
}


class BusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bus'

    def ready(self):
        # print("Connecting post_migrate signal for predata population.")
        post_migrate.connect(PopulatePreData, sender=self, weak=False)
        post_migrate.connect(AddBusSchedules, sender=self, weak=False)


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
        try:
            bus_route_directions_service_result = busRoute.getGmapsDirectionsServiceResult()
            busRoute.gmaps_polyline_encoding = bus_route_directions_service_result.getGmapsPolylineEncoding()
            busRoute.gmaps_polyline_bounds = bus_route_directions_service_result.getGmapsPolylineBounds()
        except:
            print(f'An error occurred while fetching the Google Maps Polyline. Route : {bus_route["name"]}')

        if busRoute.name in std_color_codes:
            busRoute.color_code = std_color_codes[busRoute.name]
        busRoute.save()
    elif not busRoute.gmaps_polyline_encoding or not busRoute.gmaps_polyline_bounds:
        print(f'Adding gmaps polyline data. Route : {bus_route["name"]}')
        try:
            bus_route_directions_service_result = busRoute.getGmapsDirectionsServiceResult()
            busRoute.gmaps_polyline_encoding = bus_route_directions_service_result.getGmapsPolylineEncoding()
            busRoute.gmaps_polyline_bounds = bus_route_directions_service_result.getGmapsPolylineBounds()
            busRoute.save()
        except:
            print(f'An error occurred while fetching the Google Maps Polyline. Route : {bus_route["name"]}')
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
    with open(os.path.join(settings.BASE_DIR, "route_data", "allRoutes.json")) as f:
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


def get_scheduled_time(scheduled_time):
    if len(scheduled_time) > 0:
        fTime = scheduled_time.split(':')
        hour = int(fTime[0])
        minutes = int(fTime[1])
        return datetime.time(hour=hour, minute=minutes, second=0)
    return None


def addScheduleIfNotExist(route, schedules):
    from bus.models import BusStop, BusRoute, BusSchedule

    busRoute = BusRoute.objects.filter(name=route).first()
    if busRoute:
        for schedule in schedules:
            busStop = BusStop.objects.filter(stop_id=schedule["bus_stop"]).first()
            if busStop and not BusSchedule.objects.filter(bus_route_id=busRoute.id,
                                                          bus_stop_id=busStop.id,
                                                          day_of_week=schedule["day_of_week"],
                                                          scheduled_time=get_scheduled_time(
                                                              schedule["scheduled_time"])).exists():
                print(f'Adding New Schedule for {get_scheduled_time(schedule["scheduled_time"])}')
                newSchedule = BusSchedule()
                newSchedule.bus_route = busRoute
                newSchedule.bus_stop = busStop
                newSchedule.day_of_week = schedule["day_of_week"]
                newSchedule.scheduled_time = get_scheduled_time(schedule["scheduled_time"])
                newSchedule.save()


def AddBusSchedules(sender, **kwargs):

    if not settings.SYNC_BUS_SCHEDULES:
        print("SYNC_BUS_SCHEDULES set to False. Skipping bus schedule sync")
        return
    # Read json file with all the route data (bus stops and their lat, lng, etc)
    schedule_data = None
    with open(os.path.join(settings.BASE_DIR, "route_data/bus_schedules.json")) as f:
        schedule_data = json.load(f)
    for route, schedules in schedule_data.items():
        print(f'Checking schedules for {route}')
        addScheduleIfNotExist(route, schedules)
