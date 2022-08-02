import ast
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.shortcuts import render, HttpResponse

import commons.helper
from .models import Bus, BusStop, BusRoute, TransitLog, TransitLogEntry

# Socket IO
sio = settings.SIO
"""
Bus Driver page
"""


@login_required
@permission_required('bus.access_busdriver_pages', raise_exception=True)
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


def getBusRouteGmapsPolylineEncodingAJAX(request):
    """
    Returns polyline encoding (str) from Google Maps DirectionsService API
    for user-selected route.
    """
    # extract the data from the request
    user_data = ast.literal_eval(request.GET.get('data'))
    user_selected_route = user_data.get('route')
    # get the BusRoute instance and return the polyline encoding
    busRoute = BusRoute.objects.filter(id=user_selected_route).first()
    return HttpResponse(json.dumps(busRoute.gmaps_polyline_encoding))



@login_required
@permission_required('bus.access_busdriver_pages', raise_exception=True)
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
        selected_route = BusRoute.objects.filter(pk=pos_data['selected_route']).first()
        bus_lat = pos_data['latitude']
        bus_lng = pos_data['longitude']

        # Check if the bus exists already
        bus = Bus.objects.filter(driver=request.user.username).first()
        if bus is None:
            # Create a Bus and TransitLog instance
            log = TransitLog(driver=request.user.username, bus_route=selected_route)
            log.save()
            bus = Bus(driver=request.user.username, transit_log_id=log.id)
            bus.route = selected_route

        # Update the bus coordinates
        bus.latitude = bus_lat
        bus.longitude = bus_lng
        bus.save()

        # Create new TransitLogEntry
        transit_log = TransitLog.objects.get(id=bus.transit_log_id)
        new_transit_log_entry = TransitLogEntry()
        new_transit_log_entry.transit_log = transit_log
        new_transit_log_entry.latitude = bus_lat
        new_transit_log_entry.longitude = bus_lng
        new_transit_log_entry.save()

        return HttpResponse(f"Success")
    else:
        return HttpResponse("Error: Didn't receive data.")


@login_required
@permission_required('bus.access_busdriver_pages', raise_exception=True)
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


@login_required
@permission_required('bus.access_busdriver_pages', raise_exception=True)
def transit_logs_view(request):
    transit_logs = TransitLog.objects.order_by('-date_added')
    context = {'transit_logs': transit_logs}
    return render(request, 'bus/transit_logs.html', context)


@login_required
@permission_required('bus.access_busdriver_pages', raise_exception=True)
def transit_log_entries_view(request, log_id):
    transit_log = TransitLog.objects.get(id=log_id)
    entries = transit_log.transitlogentry_set.order_by('time_stamp')
    context = {'transit_log': transit_log, 'entries': entries}
    return render(request, 'bus/transit_log_entries.html', context)
