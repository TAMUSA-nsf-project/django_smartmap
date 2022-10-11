import ast
import datetime
import json
from datetime import datetime
from datetime import timedelta

import pytz
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, HttpResponse

import commons.helper
from .distancematrixcalcs import calc_duration
from .models import Bus, BusRouteDetails, BusRoute, TransitLog, TransitLogEntry, BusSchedule

BUS_SCHEDULE_INTERVAL_MINUTES = 40
"""
Bus Driver page
"""


@login_required
@permission_required('bus.access_busdriver_pages', raise_exception=True)
def busdriver_view(request):
    context = {'allRoutes': commons.helper.getAllActiveRoutesDropDown()}
    return render(request, "bus/busdriver_2.html", context)


def getScheduleDayOfWeekLetter(date):
    today = date.weekday()

    if today == 6:  # Sunday
        return "F"
    elif today == 5:  # Saturday
        return "S"
    else:  # Weekday
        return "W"


def getEstimatedTime(busStopCoord, user_selected_route, scheduled_time):
    dateNow = datetime.utcnow().astimezone(pytz.timezone('US/Central'))
    dateTime = dateNow.replace(hour=scheduled_time.hour, minute=scheduled_time.minute, second=scheduled_time.second)

    if dateTime < datetime.utcnow().astimezone(pytz.timezone('US/Central')):
        return None

    route = BusRoute.objects.filter(id=user_selected_route).first()
    startCoord = route.first_stop.getCoordinates()
    eat_for_the_stop = calc_duration(startCoord, busStopCoord, dateTime)
    # Add this value to the scheduled start time to find the time for the given stop.
    next_schedule_arrival = dateTime + timedelta(seconds=eat_for_the_stop['value'])

    # If the calculated time is in the past, move to the next schedule.
    if next_schedule_arrival < datetime.utcnow().astimezone(pytz.timezone('US/Central')):
        return None
    return next_schedule_arrival


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
    busStop = BusRouteDetails.objects.get(parent_route=user_selected_route, bus_stop__stop_id=int(user_selected_bus_stop)).bus_stop
    busStopCoord = busStop.getCoordinates()

    # filter Bus models by route (for now)
    # assumptions:  only one bus at anytime per route
    bus = Bus.objects.filter(route=user_selected_route).first()  # TODO filter for multiple busses

    if bus is None:
        if calc_schedule == 1:
            dateTimeNow = datetime.utcnow().astimezone(pytz.timezone('US/Central'))
            day_of_week = getScheduleDayOfWeekLetter(dateTimeNow)
            next_schedules = BusSchedule.objects.filter(bus_route_id=user_selected_route, day_of_week=day_of_week,
                                                        scheduled_time__hour__gte=dateTimeNow.time().hour - 1)
            est_time = None
            for schedule in next_schedules:
                est_time = getEstimatedTime(busStopCoord, user_selected_route, schedule.scheduled_time)
                if est_time is None:
                    continue
                else:
                    break
            if est_time is None:
                est_time = calculate_approximate_schedule_time(busStopCoord, user_selected_route, bus)
            result['scheduled_arrival'] = est_time.strftime("%I:%M %p on %B %d, %Y")
        return HttpResponse(json.dumps(result))

    busCoord = bus.getCoordinates()
    # send Bus obj coords and BusStop obj coords to dist matrix calc
    travelDuration = calc_duration(busCoord, busStopCoord, datetime.now())
    result['est_arrival'] = travelDuration['text']
    dateTimeNow = datetime.utcnow().astimezone(pytz.timezone('US/Central'))
    estimatedTime = dateTimeNow + timedelta(seconds=travelDuration['value'])
    result['scheduled_arrival'] = estimatedTime.strftime("%I:%M %p on %B %d, %Y")

    # return estimated arrival time result to user
    return HttpResponse(json.dumps(result))


# TODO : Needs to update this function to fetch value from db
def calculate_approximate_schedule_time(busStopCoord, user_selected_route, bus):
    next_schedule_start = ""
    if bus is not None:
        # use the bus start time for calculation
        next_schedule_start = bus.start_time
    else:
        # Calculate the number of minutes elapsed from midnight
        now = datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        total_mins_elapsed = (now - midnight).seconds // 60
        # Derive the total number of services completed. Assuming there is a service evry 40 minutes.
        no_of_schedules = total_mins_elapsed // BUS_SCHEDULE_INTERVAL_MINUTES
        # With this calculate the latest service start time
        next_schedule_start = (midnight + timedelta(minutes=no_of_schedules * BUS_SCHEDULE_INTERVAL_MINUTES))

    # Hard coding to CDT for now
    next_schedule_start = next_schedule_start.astimezone(pytz.timezone('US/Central'))

    # Now calculate the approximate travel time from the first bus stop till the selected stop.
    route = BusRoute.objects.filter(id=int(user_selected_route)).first()
    startCoord = route.first_stop.getCoordinates()
    eat_for_the_stop = calc_duration(startCoord, busStopCoord, datetime.now())
    eat_for_the_stop = int(eat_for_the_stop['text'].split(' ')[0])

    # Add this value to the scheduled start time to find the time for the given stop.
    next_schedule_start = next_schedule_start + timedelta(minutes=eat_for_the_stop)

    # If the calculated time is in the past, move to the next schedule.
    if next_schedule_start < datetime.utcnow().astimezone(pytz.timezone('US/Central')):
        next_schedule_start = next_schedule_start + timedelta(minutes=40)
    return next_schedule_start


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
            bus.start_time = datetime.utcnow()

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
