from django.shortcuts import render, HttpResponse
from collections import defaultdict
from django.conf import settings
import json
import os
import ast

from django.contrib.auth.decorators import login_required, permission_required

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


@login_required
@permission_required('bus.access_busdriver_pages', raise_exception=True)
def busdriver_view(request):
    context = {
        "route_json": json_data.keys(),
    }
    return render(request, "bus/busdriver_2.html", context)


def bus_position_ajax(request):
    """
    data format: {'selected_route': str, 'bus_lat': float, 'bus_lng': float }
    """
    if request.method == 'GET':
        pos_data = ast.literal_eval(request.GET.get('posData'))
        busses[str(request.user)] = pos_data  # TODO the driver's username is used as the key
        sio.emit("display busses", busses)
        return HttpResponse(f"Success")
    else:
        return HttpResponse("Error: Didn't receive data.")


