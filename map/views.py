import os

from collections import defaultdict

from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from django.conf import settings
import json

import socketio
sio = socketio.Server(async_mode='threading')

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


"""
AJAX testing.
"""
def ajax_view(request):
    return render(request, 'map/ajax_test_1.html')


def ajax_background_request_handler(request):
    """
    Handles ajax requests sent in background while user is on webpage rendered by ajax_view.
    :param request:
    :return:
    """
    if request.method == 'GET':
        data_attribute = request.GET.get('some_attribute')
        return HttpResponse(f"The number sent to the server via AJAX (GET) is: {data_attribute}")
    elif request.method == 'POST':
        data_attribute = request.POST.get('some_attribute')
        return HttpResponse(f"The number sent to the server via AJAX (POST) is: {data_attribute}")
    else:
        return HttpResponse("Error: Didn't receive data.")


# Location AJAX Testing
def location_view(request):
    return render(request, 'map/location_ajax_test.html')

def location_test_ajax_handler(request):
    """
    Handles ajax requests sent in background while user is on webpage rendered by ajax_view.
    :param request:
    :return:
    """
    if request.method == 'GET':
        user_lat = request.GET.get('user_lat')
        user_lng = request.GET.get('user_lng')
        return HttpResponse(f"The user's latitude is {user_lat}, longitude is {user_lng}")
    else:
        return HttpResponse("Error: Didn't receive data.")


"""
Socket testing.
"""
votes = {"yes": 0, "no": 0, "maybe": 0}
user_location = {"user_lat": "nothing yet", "user_lng": "nothing yet"}

# Basic socket testing
def socket_view(request):
    return render(request, 'map/sockettest.html', {"votes": votes, "user_location": user_location})


@sio.event
def submit_vote(sid, data):
    votes[data] += 1
    sio.emit("vote totals", votes)



# Socket testing with user location
def location_socket_view(request):
    return render(request, 'map/location_sockettest.html', {"user_location": user_location})


@sio.event
def broadcast_location(sid, data):
    # Update dictionary
    user_location["user_lat"] = data.get('user_lat')
    user_location["user_lng"] = data.get('user_lng')
    sio.emit("display location", user_location)


"""
Bus Driver page
"""

# dictionary of busses where key is the socket ID (sid)
busses = defaultdict(dict)


def busdriver_view(request):
    context = {
        "route_json": json_data.keys(),
    }
    return render(request, "map/busdriver_2.html", context)


@sio.event
def broadcast_bus(sid, data):
    # current assumptions: sid does not change for a unique client even when selected route changes (so far I've observed
    # this to be true)
    busses[sid] = data
    sio.emit("display busses", busses)

