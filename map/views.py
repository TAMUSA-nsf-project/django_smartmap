import ast
import os
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from django.conf import settings
import json

# Socket IO
import commons.helper

sio = settings.SIO

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
        "all_routes": json.dumps(commons.helper.getAllActiveRoutesDropDown())
    }
    return render(request, 'map/map_index.html', context)


def getRouteDetails(request):
    user_data = ast.literal_eval(request.GET.get('data'))
    stops = commons.helper.getRoutesDetails(user_data)
    if stops:
        stops = list(stops)
    allStops = {
        'all_stops' : stops
    }
    return HttpResponse(json.dumps(allStops))

