from django.shortcuts import render, HttpResponse
from collections import defaultdict
from django.conf import settings
import json
import os
from pathlib import Path

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



"""
Simulation File Page
"""
SIM_DIR = os.path.join(settings.BASE_DIR, "sim_files")

def simulation_view(request):
    # safely make the directory where sim files shall be stored
    Path(SIM_DIR).mkdir(exist_ok=True)
    return render(request, "bus/simulation_2.html")


import ast
def simulation_ajax(request):
    if request.method == 'GET':
        data = ast.literal_eval(request.GET.get('data'))
        formatted = {data['file_name']: data['pos_data']}
        with open(os.path.join(SIM_DIR, data['file_name'] + ".json"), "w") as f:
            json.dump(formatted, f)

        return HttpResponse(f"success")
    else:
        return HttpResponse("Error: Didn't receive data.")