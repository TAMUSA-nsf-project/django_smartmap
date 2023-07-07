import datetime
import json
import re
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

import googlemaps
from googlemaps.directions import directions

from geopy.distance import distance as geopy_distance

DEFAULT_COLOR_CODE = "#FF0000"

gmaps = googlemaps.Client(key=settings.GOOGLE_PYTHON_API_KEY)


# Create your models here.
class Bus(models.Model):
    """
    Active busses.
    """
    latitude = models.FloatField()
    longitude = models.FloatField()
    # driver = models.OneToOneField("BusDriver", on_delete=models.CASCADE)
    driver = models.CharField(max_length=100)
    route = models.ForeignKey("BusRoute", on_delete=models.DO_NOTHING)
    start_time = models.DateTimeField(default=None, blank=True, null=True)
    end_time = models.DateTimeField(default=None, blank=True, null=True)
    # transit_log_id = models.PositiveIntegerField(default=None)
    arrival_log_id = models.PositiveIntegerField(default=None)
    seat_availability = models.CharField(default="green", max_length=50)  # todo only values "green", "red", "yellow"
    eta_log_time_counter = models.PositiveIntegerField(default=0)
    latest_route_stop_index = models.PositiveSmallIntegerField(default=1)  # todo default = 0

    def getBusColorStaticUrl(self) -> str:
        """
        Returns URL to appropriate static colored bus icon based on seat availability.

        'green' = many open seats
        'yellow' = <3 open seats
        'red' = no open seats
        """
        return settings.STATIC_URL + "map/icons/" + self.seat_availability + "_bus.png"

    def getLatLngTuple(self):
        return self.latitude, self.longitude

    def getCoordinates(self):
        return self.getLatLngTuple()

    def getBusRouteDetailsSet(self):
        return self.route.busroutedetails_set.all()

    class Meta:
        verbose_name_plural = 'buses'  # django automatically capitalizes this in the admin site

    def __str__(self):
        return f"Bus {self.id}"


class BusStop(models.Model):
    stop_id = models.PositiveIntegerField()
    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def getLatLngTuple(self):
        return self.latitude, self.longitude

    def getCoordinates(self):
        return self.getLatLngTuple()

    def getGeodesicDistanceTo(self, coords):
        return geopy_distance(coords, self.getCoordinates())

    def __str__(self):
        return self.name


class BusRoute(models.Model):
    # route_id = models.IntegerField()  # don't need, not in json, django auto creates an id field
    name = models.CharField(max_length=200)
    first_stop = models.ForeignKey("BusStop", on_delete=models.CASCADE, related_name="first_stop")
    last_stop = models.ForeignKey("BusStop", on_delete=models.CASCADE, related_name="last_stop")
    active = models.BooleanField(default=False)
    color_code = models.CharField(max_length=10, default=DEFAULT_COLOR_CODE)
    gmaps_polyline_encoding = models.TextField(default="")
    gmaps_polyline_bounds = models.CharField(default="", max_length=200)

    def getDisplayName(self):
        """
        Because route names in the JSON file may contain undesirable text (like "(reverse)") for displaying in the UI,
        this method is used to clean it up.
        """
        display_name = self.name
        if "reverse" in display_name:
            display_name = re.sub(r"\s*\(reverse\)", "", display_name)
        return display_name

    def getGmapsDirectionsServiceResult(self):
        """
        Returns an object representing a Google Map's DirectionsService API result.
        """
        origin_coords = self.first_stop.getCoordinates()
        dest_coords = self.last_stop.getCoordinates()
        res = directions(gmaps, origin=origin_coords, destination=dest_coords, mode="transit", transit_mode="bus")
        if not res:
            raise ValueError("DirectionsService API result is empty")

        class GmapsDirectionsServiceResult:

            def __init__(self):
                self._res = res

            def getGmapsPolylineEncoding(self) -> str:
                """
                Returns the ascii string encoding of the polyline calculated by Google's Directions Service API.
                The directions result may return multiple results. We are interested in the TRANSIT part of it.
                """
                polyline_encoding = None
                if self._res[0]['legs'] and self._res[0]['legs'][0]['steps']:
                    for step in self._res[0]['legs'][0]['steps']:
                        if step['travel_mode'] == 'TRANSIT':
                            polyline_encoding = step['polyline']['points']
                            break
                if not polyline_encoding:
                    raise ValueError("BusRoute Gmaps polyline encoding is empty.")
                return polyline_encoding

            def getGmapsPolylineBounds(self) -> dict:
                """
                Returns the bounds of the polyline as determined by Google's Directions Service API.
                Example: {'northeast': {'lat': 29.422504, 'lng': -98.4895075}, 'southwest': {'lat': 29.3468565, 'lng': -98.5465827}}
                """
                return self._res[0]['bounds']

            def __repr__(self):
                return str(self._res)

        return GmapsDirectionsServiceResult()

    def __str__(self):
        return self.name


class BusRouteDetails(models.Model):
    parent_route = models.ForeignKey("BusRoute", on_delete=models.CASCADE)
    bus_stop = models.ForeignKey("BusStop", on_delete=models.CASCADE)
    route_index = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name_plural = 'bus route details'

    def __str__(self):
        return f"{self.parent_route.name}: {self.bus_stop.name}"


class BusDriver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ("access_busdriver_pages", "Can access bus driver pages.")
        ]

    def __str__(self):
        return self.user.username


def default_time():
    return datetime.time(hour=23, minute=59, second=59)


def getDayOfWeek(day_of_week):
    if day_of_week == "W":
        return "Weekday"
    elif day_of_week == "S":
        return "Saturday"
    elif day_of_week == "F":
        return "Sunday"
    else:
        return ""


class BusSchedule(models.Model):
    bus_route = models.ForeignKey("BusRoute", on_delete=models.CASCADE)
    bus_stop = models.ForeignKey("BusStop", on_delete=models.CASCADE)
    # W = WeekDay (Monday - Friday), S = Saturday , F = Sunday
    day_of_week = models.CharField(max_length=1)
    scheduled_time = models.TimeField(default=default_time)

    def __str__(self):
        return f"{self.bus_route.name}, {self.bus_stop.name}, {self.scheduled_time.strftime('%I:%M %p')}, {getDayOfWeek(self.day_of_week)}"


class TransitLog(models.Model):
    # bus_driver = models.ForeignKey("BusDriver", on_delete=models.DO_NOTHING)
    driver = models.CharField(max_length=100)
    bus_route = models.ForeignKey("BusRoute", on_delete=models.DO_NOTHING)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bus_route.name}, {self.driver}, {self.date_added.strftime('%Y-%m-%d %H:%M:%S')}"


class TransitLogEntry(models.Model):
    transit_log = models.ForeignKey("TransitLog", on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.time_stamp}, Lat: {self.latitude}, Lng: {self.longitude}"


# todo: these can be moved to a new app
class BusArrivalLog(models.Model):
    driver = models.CharField(max_length=100)  # for now just using name of bus driver
    route_id = models.PositiveSmallIntegerField(default=None)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Route: {self.route_id}"

    def __repr__(self):
        self_str = str(self)
        return self_str if len(self_str) < 50 else self_str[:50] + "..."


class BusArrivalLogEntry(models.Model):
    bus_arrival_log = models.ForeignKey("BusArrivalLog", on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    time_stamp = models.CharField(max_length=100, blank=True, null=True)
    bus_stop_id = models.PositiveIntegerField(default=None)
    # scheduled_arrival_time = models.DateTimeField(default=None)  # todo
    estimated_arrival_time = models.CharField(max_length=100)
    api_response_value = models.CharField(max_length=100, blank=True, null=True)
    stop_skipped_time = models.CharField(max_length=100, blank=True, null=True)
    actual_arrival_time = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.time_stamp.strftime("%H:%M:%S")}, BusStopID: {self.bus_stop_id}, ETA: {self.estimated_arrival_time}, ATA: {self.actual_arrival_time}'

    def __repr__(self):
        self_str = str(self)
        return self_str if len(self_str) < 50 else self_str[:50] + "..."
