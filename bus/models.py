import datetime
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
    transit_log_id = models.PositiveIntegerField(default=None)
    seat_availability = models.CharField(default="green", max_length=50)  # todo only values "green", "red", "yellow"
    latest_route_stop_index = models.PositiveSmallIntegerField(default=1)

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

    def getNearestRouteStopIndex(self, start_index=1):
        """
        Use geopy to loop through the bus stops in the current route for the nearest stop within 50 meters and return
        its index, otherwise return -1.
        """

        if start_index < 1:
            raise ValueError("Route indexing starts at 1")

        bus_route_details = self.route.busroutedetails_set.all()
        for i in range(start_index - 1, len(bus_route_details)):
            brd_obj = bus_route_details[i]
            bus_stop = brd_obj.bus_stop
            dist_between = geopy_distance(self.getCoordinates(), bus_stop.getCoordinates()).m
            if dist_between < 50:
                return brd_obj.route_index
        return -1

    def updateLatestRouteStopIndex(self):
        """
        Updates latest_route_stop_index field using getNearestRouteStopIndex
        """
        nearest_route_stop_index = self.getNearestRouteStopIndex(self.latest_route_stop_index)
        if nearest_route_stop_index > -1 and nearest_route_stop_index != self.latest_route_stop_index:
            self.latest_route_stop_index = nearest_route_stop_index

    def getBusRouteDetails(self):
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

        class GmapsDirectionsServiceResult:
            def __init__(self):
                self._res = res

            def getGmapsPolylineEncoding(self) -> str:
                """
                Returns the ascii string encoding of the polyline calculated by Google's Directions Service API.
                """
                polyline_encoding = self._res[0]['overview_polyline']['points']
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
    route = models.ForeignKey("BusRoute", on_delete=models.DO_NOTHING)


class BusArrivalLogEntry(models.Model):
    bus_arrival_log = models.ForeignKey("BusArrivalLog", on_delete=models.CASCADE)
    bus = models.ForeignKey("Bus", on_delete=models.DO_NOTHING)  # todo how will a bus be represented if instance is
    # deleted?
    time_stamp = models.DateTimeField(auto_now_add=True)
    bus_stop_id = models.PositiveIntegerField(default=None)
    estimated_arrival_time = models.DateTimeField(default=None)
    actual_arrival_time = models.DateTimeField(default=None)
