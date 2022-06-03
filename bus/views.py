from django.shortcuts import render
from collections import defaultdict
from django.conf import settings
import json
import os

# Socket IO
sio = settings.SIO

# Create your views here.

# Read json file with all the route data (bus stops and their lat, lng, etc)
with open(os.path.join(settings.BASE_DIR, "route_data/allRoutes.json")) as f:
    json_data = json.load(f)

# to be passed to template
json_routes = json.dumps(json_data)


"""
Bus Driver page
"""

# dictionary of busses where key is the socket ID (sid)
busses = defaultdict(dict)


def busdriver_view(request):
    context = {
        "route_json": json_data.keys(),
    }
    return render(request, "bus/busdriver_2.html", context)




import googlemaps
from datetime import datetime
from googlemaps.distance_matrix import distance_matrix


# updates json_data dict as well
def calc_est_arrival_times(data):
    """
    TODO Figure out way around Distance Matrix API usage limit: Maximum of 25 origins or 25 destinations per request
    Routes such as 'Route 51' have more than 25 stops and will cause error: "googlemaps.exceptions.ApiError: MAX_DIMENSIONS_EXCEEDED"
    """
    # data format: {'selected_route': str, 'bus_lat': float, 'bus_lng': float }

    bus_route = data["selected_route"]
    stop_data = json_data[bus_route]
    stops_latlng = [(stop["Lat"], stop["Lng"]) for stop in stop_data]

    gmaps = googlemaps.Client(key=settings.GOOGLE_PYTHON_API_KEY)
    res = distance_matrix(gmaps, origins=(data['bus_lat'], data['bus_lng']), destinations=stops_latlng, transit_mode="bus",
                          departure_time=datetime.now())

    for i in range(len(stop_data)):
        stop_data[i]['est_arrival'] = res['rows'][0]['elements'][i]['duration']['text']

    return {bus_route: stop_data}





@sio.event
def broadcast_bus(sid, data):
    # current assumptions: sid does not change for a unique client even when selected route changes (so far I've observed
    # this to be true)
    # data format: {'selected_route': str, 'bus_lat': float, 'bus_lng': float }
    busses[sid] = data
    sio.emit("display busses", busses)
    res = calc_est_arrival_times(data)
    sio.emit("update arrival times", res)


# in new socket func, data comes in, gets sent to some functions for processing and a new set of data is sent out