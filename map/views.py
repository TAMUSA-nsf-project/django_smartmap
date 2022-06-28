import os
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from django.conf import settings
import json

# Socket IO
sio = settings.SIO

# Read json file with all the route data (bus stops and their lat, lng, etc)
with open(os.path.join(settings.BASE_DIR, "route_data/allRoutes.json")) as f:
    json_data = json.load(f)

# to be passed to template
json_routes = json.dumps(json_data)

# Create your views here.

"""
Google Map
"""
def map_hello_world(request):
    """
    Renders a page with embedded Google map. Passes variables to the associated html template via dictionary
    'context'. The URL associated with this view function is defined in urls.py.
    """

    context = {
        "google_api_key": settings.GOOGLE_MAP_API_KEY,
        "lat_coord": 29.4190,
        "lng_coord": -98.4836,
        "route_json": json_routes
    }
    return render(request, 'map/map_index.html', context)

