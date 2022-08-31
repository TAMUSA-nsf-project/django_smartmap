import ast
import os
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from django.conf import settings
import json

import commons.helper

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


def getRouteDetailsAJAX(request):
    user_data = ast.literal_eval(request.GET.get('data'))
    stops = commons.helper.getRoutesDetails(user_data)
    if stops:
        stops = list(stops)
    allStops = {
        'all_stops': stops
    }
    return HttpResponse(json.dumps(allStops))


def getBusColorDescriptionAJAX(request):
    static_base_url = settings.STATIC_URL
    if settings.DEBUG:
        static_base_url = request.build_absolute_uri('/')[:-1].strip("/") + '/static/'

    result = [
        {
            'icon': f'{static_base_url}map/icons/red_bus.png',
            'description': "No Seats Available"
        },
        {
            'icon': f'{static_base_url}map/icons/yellow_bus.png',
            'description': "Less than 3 seats Available"
        },
        {
            'icon': f'{static_base_url}map/icons/green_bus.png',
            'description': "More than 3 seats Available"
        }
    ]
    return HttpResponse(json.dumps(result))
