import ast
import datetime
import json
from datetime import datetime
from datetime import timedelta
from django.utils import timezone

import pytz
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, HttpResponse

import commons.helper
from .distancematrixcalcs import calc_duration
from .models import Bus, BusRoute, BusRouteDetails, BusSchedule
from .models import TransitLog, BusArrivalLog, BusArrivalLogEntry

BUS_SCHEDULE_INTERVAL_MINUTES = 40

BUS_STOP_ARRIVAL_PROXIMITY = 10  # meters
ARRIVAL_LOG_FREQUENCY = 30  # seconds

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
    busStop = BusRouteDetails.objects.get(parent_route=user_selected_route,
                                          bus_stop__stop_id=int(user_selected_bus_stop)).bus_stop
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
        ajax_data = ast.literal_eval(request.GET.get('posData'))
        selected_route = ajax_data['selected_route']
        bus_lat = ajax_data['latitude']
        bus_lng = ajax_data['longitude']

        # Get current time
        # datetime_now = datetime.utcnow()  # original code
        # datetime_now = datetime.utcnow().astimezone(pytz.timezone('US/Central'))
        datetime_now = timezone.now()

        # Get BusRoute instance from db
        busRoute = BusRoute.objects.filter(pk=selected_route).first()

        # Check if the Bus instance exists already
        bus = Bus.objects.filter(driver=request.user.username).first()

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
            bus.last_eta_logged_time = datetime_now
            bus.latest_route_stop_index = 0  # assumes bus hasn't first stop yet, allows its arrival to be logged

        # Update the bus coordinates and timekeeping
        bus.latitude = bus_lat
        bus.longitude = bus_lng
        last_eta_logged_time = bus.last_eta_logged_time
        bus.save()

        # Get BusRouteDetails set
        busRouteDetails_set = bus.getBusRouteDetailsSet()

        """ 
        The following if-clause is executed at a frequency defined on the frontend (currently every ~2 sec) 
        """
        if bus.latest_route_stop_index < len(busRouteDetails_set):

            # Look for proximity to a bus stop starting at last visited stop (if applicable)
            nextBusStopIdx = None
            for i in range(bus.latest_route_stop_index, len(busRouteDetails_set)):
                if busRouteDetails_set[i].bus_stop.getGeodesicDistanceTo(
                        bus.getCoordinates()).m < BUS_STOP_ARRIVAL_PROXIMITY:
                    nextBusStopIdx = i
                    break

            # Check if arrived at next stop
            if nextBusStopIdx is not None:  # None-check required because nextBusStopIdx can be 0
                # Get next stop
                nextBusRouteDetail = busRouteDetails_set[nextBusStopIdx]  # get BusRouteDetails obj at index nextB...
                addArrivalTimeForStopByID(bus, nextBusRouteDetail.bus_stop.stop_id, datetime_now)

                # Update bus's latest route stop index
                bus.latest_route_stop_index = nextBusRouteDetail.route_index  # route_index starts at 1
                bus.save(update_fields=['latest_route_stop_index'])

        """ 
        The following inner if-clause is executed at frequency ARRIVAL_LOG_FREQUENCY defined above
        """
        # must check latest_route_stop_index again because previous if-clause can change it
        if bus.latest_route_stop_index < len(busRouteDetails_set) and last_eta_logged_time is not None:
            delta = datetime_now - last_eta_logged_time

            if delta.seconds > ARRIVAL_LOG_FREQUENCY:  # be aware that .seconds is capped at 86400

                # Get the BusArrivalLog instance
                arrivalLog = BusArrivalLog.objects.filter(id=bus.arrival_log_id).first()

                # Update the time value only here. So that the interval will be calculated properly
                bus.last_eta_logged_time = datetime_now
                bus.save()

                for i in range(bus.latest_route_stop_index, len(busRouteDetails_set)):
                    busStop = busRouteDetails_set[i].bus_stop
                    res = calc_duration(bus.getCoordinates(), busStop.getCoordinates(), datetime_now)
                    estimatedTime = datetime_now + timedelta(seconds=res['value'])

                    # create ArrivalLogEntry
                    arrivalLogEntry = BusArrivalLogEntry()
                    arrivalLogEntry.bus_arrival_log = arrivalLog
                    arrivalLogEntry.time_stamp = datetime_now
                    arrivalLogEntry.bus_stop_id = busStop.stop_id
                    arrivalLogEntry.bus_driver = bus.driver
                    arrivalLogEntry.latitude = bus.latitude
                    arrivalLogEntry.longitude = bus.longitude
                    arrivalLogEntry.estimated_arrival_time = estimatedTime.strftime("%H:%M:%S")  # 24-hr format
                    arrivalLogEntry.save()

        # Data to pass back to frontend
        # create indexing var for busRouteDetails_set to get name of last bus stop
        lastStopIdx = bus.latest_route_stop_index
        if lastStopIdx > 0:
            lastStopIdx -= 1  # decrement for zero-based indexing of busRouteDetails_set

        return HttpResponse(json.dumps({'status': "Success",
                                        'last_stop_idx': bus.latest_route_stop_index,
                                        'last_stop_name': busRouteDetails_set[lastStopIdx].bus_stop.name}))
    else:
        return HttpResponse(json.dumps({'status': "Did not receive data."}))


def addArrivalTimeForStopByID(bus: Bus, bus_stop_id: int, datetime_now):
    # Get or create a BusArrivalLog instance
    arrivalLog = BusArrivalLog.objects.filter(id=bus.arrival_log_id).first()
    # create ArrivalLogEntry
    arrivalLogEntry = BusArrivalLogEntry()
    arrivalLogEntry.bus_arrival_log = arrivalLog
    arrivalLogEntry.time_stamp = datetime_now
    arrivalLogEntry.bus_stop_id = bus_stop_id
    arrivalLogEntry.latitude = bus.latitude
    arrivalLogEntry.longitude = bus.longitude
    arrivalLogEntry.actual_arrival_time = str(datetime_now)
    arrivalLogEntry.save()


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
    btn_data = int(data.get('choice'))
    bus = Bus.objects.filter(driver=request.user.username).first()
    if bus and btn_data > 0:
        bus.latest_route_stop_index = btn_data
        bus.save()
        busStopId = BusRouteDetails.objects.filter(parent_route_id=bus.route_id,
                                                   route_index=btn_data).first().bus_stop.stop_id
        addArrivalTimeForStopByID(bus, busStopId, timezone.now())

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
