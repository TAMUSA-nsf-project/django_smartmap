import json, os

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_smartmap.settings'

import django

django.setup()

from django.conf import settings

from bus.models import BusStop, BusRoute, BusRouteDetails

# Read json file with all the route data (bus stops and their lat, lng, etc)
with open(os.path.join(settings.BASE_DIR, "route_data/allRoutes.json")) as f:
    json_data = json.load(f)

STATUS_MSG_BASE = "creating"
Stop_Name_KEY = "Stop Name"

# BusStop instances
for route, bus_stop_list in json_data.items():
    for stop_dict in bus_stop_list:
        stop_name = stop_dict[Stop_Name_KEY]
        try:
            busStop = BusStop.objects.get(name=stop_name)
        except BusStop.DoesNotExist:
            print(STATUS_MSG_BASE + f" BusStop instance for {stop_name}")
            busStop = BusStop()
            busStop.name = stop_name
            busStop.stop_id = stop_dict["Stop Number"]
            busStop.latitude = stop_dict["Lat"]
            busStop.longitude = stop_dict["Lng"]
            busStop.save()

# BusRoute instances
for route, bus_stop_list in json_data.items():
    first_stop_name = bus_stop_list[0][Stop_Name_KEY]
    last_stop_name = bus_stop_list[-1][Stop_Name_KEY]
    try:
        busRoute = BusRoute.objects.get(name=route)
    except BusRoute.DoesNotExist:
        print(STATUS_MSG_BASE + f" BusRoute instance for {route}")
        busRoute = BusRoute()
        busRoute.name = route
        busRoute.first_stop = BusStop.objects.get(name=first_stop_name)
        busRoute.last_stop = BusStop.objects.get(name=last_stop_name)
        busRoute.save()

# BusRouteStop instances
for route, bus_stop_list in json_data.items():
    parentRoute = BusRoute.objects.get(name=route)
    for stop_dict in bus_stop_list:
        busStop = BusStop.objects.get(name=stop_dict[Stop_Name_KEY])
        route_index = stop_dict["Order on Route"]
        try:
            busRouteStop = BusRouteDetails.objects.get(parent_route__name=route,
                                                       bus_stop__name=stop_dict[Stop_Name_KEY])
        except BusRouteDetails.DoesNotExist:
            print(STATUS_MSG_BASE + f" BusRouteDetails instance for {stop_dict[Stop_Name_KEY]}")
            busRouteStop = BusRouteDetails()
            busRouteStop.parent_route = parentRoute
            busRouteStop.bus_stop = busStop
            busRouteStop.route_index = route_index
            busRouteStop.save()

print("Done")
