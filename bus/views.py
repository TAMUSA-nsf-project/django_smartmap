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


from .distancematrixcalcs import calc_est_arrival_times

@sio.event
def broadcast_bus(sid, socket_data):
    # current assumptions: sid does not change for a unique client even when selected route changes (so far I've observed
    # this to be true)
    # data format: {'selected_route': str, 'bus_lat': float, 'bus_lng': float }
    busses[sid] = socket_data
    sio.emit("display busses", busses)
    res = calc_est_arrival_times(socket_data, json_data)
    sio.emit("update arrival times", res)
