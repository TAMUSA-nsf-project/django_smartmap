import ast
import datetime
import json
from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

import pytz
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, HttpResponse

import commons.helper
from .distancematrixcalcs import calc_duration, calc_est_arrival_times
from .models import Bus, BusRoute, BusRouteDetails, BusSchedule
from .models import TransitLog, BusArrivalLog, BusArrivalLogEntry

BUS_SCHEDULE_INTERVAL_MINUTES = 40

BUS_STOP_ARRIVAL_PROXIMITY = 10  # meters
ARRIVAL_LOG_FREQUENCY = 60  # seconds

"""
Bus Driver page
"""


@login_required
@permission_required('bus.access_busdriver_pages', raise_exception=True)
def busdriver_view(request):
    context = {'allRoutes': commons.helper.getAllActiveRoutesDropDown(),
               'google_api_key': settings.GOOGLE_MAP_API_KEY}
    return render(request, "bus/busdriver_2.html", context)


def getScheduleDayOfWeekLetter(date):
    today = date.weekday()

    if today == 6:  # Sunday
        return "F"
    elif today == 5:  # Saturday
        return "S"
    else:  # Weekday
        return "W"


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
    calc_schedule = user_data.get('calc_schedule')

    result = {
        'est_arrival': "",
        'scheduled_arrival': ""
    }

    # TODO filter BusRoute models

    # get BusStop instance
    busStop = BusRouteDetails.objects.get(parent_route=user_selected_route,
                                          bus_stop__stop_id=int(user_selected_bus_stop)).bus_stop
    busStopCoord = busStop.getCoordinates()

    # filter Bus models by route (for now)
    # assumptions:  only one bus at anytime per route
    bus = Bus.objects.filter(route=user_selected_route).first()  # TODO filter for multiple busses

    dateTimeNow = datetime.now()
    day_of_week = getScheduleDayOfWeekLetter(dateTimeNow)
    next_arrival = BusSchedule.objects.filter(bus_route_id=user_selected_route, day_of_week=day_of_week,
                                              bus_stop=busStop,
                                              scheduled_time__gte=dateTimeNow.time().strftime('%H:%M:%S')).first()
    if next_arrival is not None:
        result[
            'scheduled_arrival'] = f'{next_arrival.scheduled_time.strftime("%I:%M %p")} on {dateTimeNow.date().strftime("%B %d, %Y")}'
    if bus is None:
        return HttpResponse(json.dumps(result))

    busCoord = bus.getCoordinates()
    # send Bus obj coords and BusStop obj coords to dist matrix calc
    travelDuration = calc_duration(busCoord, busStopCoord)
    if 'duration' in travelDuration['rows'][0]['elements'][0].keys():
        result['est_arrival'] = travelDuration['rows'][0]['elements'][0]['duration']['text']

    # return estimated arrival time result to user
    return HttpResponse(json.dumps(result))


def getActiveBussesOnRouteAJAX(request):
    # extract the data from the request
    user_data = ast.literal_eval(request.GET.get('data'))
    user_selected_route = user_data.get('route')

    # filter for all busses active on user-selected route
    busObjs = Bus.objects.filter(route=user_selected_route)

    # bus data to send back to client
    bus_data = {bus.id: {'selected_route': bus.route.pk, 'bus_lat': bus.latitude, 'bus_lng': bus.longitude,
                         'bus_color': bus.getBusColorStaticUrl()} for bus in busObjs}

    return HttpResponse(json.dumps(bus_data))

def getAllActiveBussesAJAX(request):
    # filter for all busses active on user-selected route
    busObjs = Bus.objects.all()

    # bus data to send back to client
    bus_data ={}
    for bus in busObjs:
        if bus.route.pk in bus_data:
            bus_data[bus.route.pk].append({'bus_id': bus.id, 'bus_lat': bus.latitude, 'bus_lng': bus.longitude,
                         'bus_color': bus.getBusColorStaticUrl(), 'title': f'{bus.driver} - {bus.route.name}'})
        else:
            bus_data[bus.route.pk] = [{'bus_id': bus.id, 'bus_lat': bus.latitude, 'bus_lng': bus.longitude,
                         'bus_color': bus.getBusColorStaticUrl(), 'title': f'{bus.driver} - {bus.route.name}'}]

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

    to_send = {'polyline_encoding': busRoute.gmaps_polyline_encoding,
               'polyline_bounds': ast.literal_eval(busRoute.gmaps_polyline_bounds)}

    return HttpResponse(json.dumps(to_send))


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
        ajax_data = ast.literal_eval(request.GET.get('posData'))
        selected_route = ajax_data['selected_route']
        bus_lat = ajax_data['latitude']
        bus_lng = ajax_data['longitude']
        active_bus_id = ajax_data['active_bus_id']

        # Get current time
        # datetime_now = datetime.utcnow()  # original code
        # time_zone = pytz.timezone('US/Central')
        datetime_now = datetime.now()
        # datetime_now = timezone.now()

        # Get BusRoute instance from db
        busRoute = BusRoute.objects.filter(pk=selected_route).first()

        # Check if the Bus instance exists already
        if active_bus_id != -1:
            bus = Bus.objects.filter(pk=active_bus_id).first()
        else:
            bus = Bus.objects.filter(driver=request.user.username,route_id=selected_route).first()

        if bus is None:
            # Create BusArrivalLog
            arrivalLog = BusArrivalLog(route_id=busRoute.id)
            arrivalLog.driver = request.user.username
            arrivalLog.save()

            # Create a Bus instance
            bus = Bus(driver=request.user.username)
            bus.route = busRoute
            bus.arrival_log_id = arrivalLog.id
            bus.start_time = datetime_now
            bus.latest_route_stop_index = 0  # assumes bus hasn't first stop yet, allows its arrival to be logged

        # Update the bus coordinates and timekeeping
        bus.latitude = bus_lat
        bus.longitude = bus_lng
        bus.eta_log_time_counter += 1
        bus.save()

        """ 
        The following inner if-clause is executed at frequency ARRIVAL_LOG_FREQUENCY defined above
        """
        # multiply 2 because of the 2-second interval in front end.
        if settings.LOG_ETA and ( bus.eta_log_time_counter * 2 > ARRIVAL_LOG_FREQUENCY):  # be aware that .seconds is capped at 86400

            eta_responses = calc_est_arrival_times(bus.route, bus.latitude, bus.longitude, bus.latest_route_stop_index)
            # Get the BusArrivalLog instance
            arrivalLog = BusArrivalLog.objects.filter(id=bus.arrival_log_id).first()

            # Reset the counter
            bus.eta_log_time_counter = 0
            bus.save()

            for bus_stop_id, response in eta_responses.items():
                # print(response)
                # create ArrivalLogEntry
                arrivalLogEntry = BusArrivalLogEntry()
                arrivalLogEntry.bus_arrival_log = arrivalLog
                arrivalLogEntry.time_stamp = datetime_now
                arrivalLogEntry.bus_stop_id = bus_stop_id
                arrivalLogEntry.bus_driver = bus.driver
                arrivalLogEntry.latitude = bus.latitude
                arrivalLogEntry.longitude = bus.longitude
                arrivalLogEntry.api_response_value = response['rows'][0]['elements'][0]['duration']['text']
                estimated_time = datetime_now + timedelta(
                    seconds=response['rows'][0]['elements'][0]['duration']['value'])
                arrivalLogEntry.estimated_arrival_time = estimated_time.strftime("%I:%M %p")  # 12-hr format
                arrivalLogEntry.save()

        return HttpResponse(json.dumps({'status': "Success",
                                        'last_stop_idx': bus.latest_route_stop_index,
                                        'active_bus_id': bus.id}))
    else:
        return HttpResponse(json.dumps({'status': "Did not receive data."}))


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
def updateBusSeatAvailabilityAJAX(request):
    data = ast.literal_eval(request.GET.get('data'))
    btn_data = data.get('choice')

    bus = Bus.objects.filter(driver=request.user.username).first()
    if bus:
        bus.seat_availability = btn_data
        bus.save()

    return HttpResponse("Success")


@login_required
@permission_required('bus.access_busdriver_pages', raise_exception=True)
def updateLastBusStopManualAJAX(request):
    data = ast.literal_eval(request.GET.get('data'))

    bus = Bus.objects.filter(driver=request.user.username).first()
    busStop = data.get('bus_stop')
    busStopIndex = data.get('bus_stop_index')
    is_arrived = bool(data.get('is_arrived'))

    # Get or create a BusArrivalLog instance
    arrivalLog = BusArrivalLog.objects.filter(id=bus.arrival_log_id).first()
    # create ArrivalLogEntry
    arrivalLogEntry = BusArrivalLogEntry()
    arrivalLogEntry.bus_arrival_log = arrivalLog

    datetime_now = datetime.now()

    arrivalLogEntry.time_stamp = datetime_now
    arrivalLogEntry.bus_stop_id = busStop
    arrivalLogEntry.latitude = bus.latitude
    arrivalLogEntry.longitude = bus.longitude
    if is_arrived:
        arrivalLogEntry.actual_arrival_time = str(datetime_now)
    else:
        arrivalLogEntry.stop_skipped_time = str(datetime_now)
    arrivalLogEntry.save()

    bus.latest_route_stop_index = busStopIndex
    bus.save()

    return HttpResponse("Success")


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


@login_required
@permission_required('bus.access_busdriver_pages', raise_exception=True)
def downloadTransitLogCSV_AJAX(request):
    log_id = ast.literal_eval(request.GET.get('data'))
    transit_log = TransitLog.objects.get(id=log_id)
    entries = transit_log.transitlogentry_set.order_by('time_stamp')
    data = [{'time_stamp': str(entry.time_stamp), 'latitude': str(entry.latitude), 'longitude': str(entry.longitude)}
            for entry in entries]
    filename = f"{transit_log.bus_route.name}-{transit_log.driver}-{transit_log.date_added.strftime('%Y-%m-%d_%H-%M-%S')}"
    return HttpResponse(json.dumps({'filename': filename, 'json_data': data}))


@login_required
# @permission_required('bus.access_busdriver_pages', raise_exception=True)
def admin_view(request):
    context = {'allRoutes': commons.helper.getAllActiveRoutesDropDown(),
               'google_api_key': settings.GOOGLE_MAP_API_KEY}
    return render(request, "bus/all_routes_admin_view.html", context)