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


def getRouteDetailsAJAX(request):
    user_data = ast.literal_eval(request.GET.get('data'))
    stops = commons.helper.getRoutesDetails(user_data)
    if stops:
        stops = list(stops)
    allStops = {
        'all_stops': stops
    }
    return HttpResponse(json.dumps(allStops))


import googlemaps
from googlemaps.directions import directions

gmaps = googlemaps.Client(key=settings.GOOGLE_PYTHON_API_KEY)


def calc_route_directions(route_id):
    stops = list(commons.helper.getRoutesDetails(route_id))
    route = []
    for i in range(len(stops) - 1):
        origin_coords = (stops[i]['BusStopLatitude'], stops[i]['BusStopLongitude'])
        dest_coords = (stops[i + 1]['BusStopLatitude'], stops[i + 1]['BusStopLongitude'])
        res = directions(gmaps, origin=origin_coords, destination=dest_coords, mode="transit", transit_mode="bus")
        print(res)
        # polyline = res[0]['overview_polyline']['points']
        # legs = res[0]['legs']
        # for leg in legs:
        #     steps = leg['steps']
        #     for step in steps:
        #         print(step)
    return route


def getRouteDirectionsAJAX(request):
    user_selected_route_id = ast.literal_eval(request.GET.get('data'))
    res = calc_route_directions(user_selected_route_id)
    return HttpResponse(json.dumps(res))
