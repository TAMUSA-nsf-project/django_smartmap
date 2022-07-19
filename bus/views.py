from django.shortcuts import render, HttpResponse
from collections import defaultdict
from django.conf import settings
import json
import os
import ast
from django.utils.timezone import utc

import commons.helper
from .models import Bus, BusDriver, BusStop, BusRoute

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


@login_required
# @permission_required('bus.access_busdriver_pages', raise_exception=True)
def busdriver_view(request):
    context = {'allRoutes': commons.helper.getAllActiveRoutesDropDown()}
    return render(request, "bus/busdriver_2.html", context)


from .distancematrixcalcs import calc_duration
from datetime import datetime


def getEstimatedArrivalAJAX(request):
    """
    Called by BusStop js class method. User is requesting position of bus(es) for a route.
    :param request:
    :return:
    """
    # extract data from request,  route and bus_stop ID
    user_data = ast.literal_eval(request.GET.get('data'))
    user_selected_route = user_data.get('route')
    user_selected_bus_stop = user_data.get('bus_stop_id')

    # TODO filter BusRoute models

    # filter Bus models by route (for now)
    # assumptions:  only one bus at anytime per route
    bus = Bus.objects.filter(route=user_selected_route).first()  # TODO filter for multiple busses
    if bus is None:
        return HttpResponse("There are no active buses on this route.")

    busCoord = (bus.latitude, bus.longitude)

    # get BusStop instance
    busStop = BusStop.objects.get(stop_id=int(user_selected_bus_stop))
    busStopCoord = (busStop.latitude, busStop.longitude)

    # send Bus obj coords and BusStop obj coords to dist matrix calc
    res = calc_duration(busCoord, busStopCoord, datetime.now())

    # return estimated arrival time result to user
    return HttpResponse(res)


def getActiveBussesOnRouteAJAX(request):
    # extract the data from the request
    user_data = ast.literal_eval(request.GET.get('data'))
    user_selected_route = user_data.get('route')

    # filter for all busses active on user-selected route
    busObjs = Bus.objects.filter(route=user_selected_route)

    # bus data to send back to client
    bus_data = {bus.id: {'selected_route': bus.route.pk, 'bus_lat': bus.latitude, 'bus_lng': bus.longitude} for bus in
                busObjs}

    return HttpResponse(json.dumps(bus_data))


@login_required
# @permission_required('bus.access_busdriver_pages', raise_exception=True)
def bus_position_ajax(request):
    """
    data format:
    {
         'selected_route': routeSelect.value,
         'latitude': geolocationCoordinates.latitude,
         'longitude': geolocationCoordinates.longitude,
         'accuracy': geolocationCoordinates.accuracy,
         'speed': geolocationCoordinates.speed,
         'heading': geolocationCoordinates.heading
     }
    """
    if request.method == 'GET':
        # extract bus position out of request
        pos_data = ast.literal_eval(request.GET.get('posData'))
        selected_route = pos_data['selected_route']
        bus_lat = pos_data['latitude']
        bus_lng = pos_data['longitude']

        # update bus pos in db (todo: push this task to async queue)
        bus = Bus.objects.filter(driver=request.user.username).first()
        if bus is None:
            # Add the bus details
            bus = Bus(driver=request.user.username)
            bus.route = BusRoute.objects.filter(pk=selected_route).first()
        # Update the location details
        bus.latitude = bus_lat
        bus.longitude = bus_lng

        bus.save()

        return HttpResponse(f"Success")
    else:
        return HttpResponse("Error: Didn't receive data.")



@login_required
def deleteBusHasEndedBroadcastAJAX(request):
    """
    Deletes a bus instance in the database if the driver has ended their broadcast session.
    """
    if request.method == 'GET':
        bus = Bus.objects.filter(driver=request.user.username).first()
        if bus is not None:
            bus.delete()
        return HttpResponse(f"Success")
    else:
        return HttpResponse("Error: Didn't receive data.")